#!/usr/bin/perl

use strict;
use warnings;
use Fcntl qw(O_CREAT O_EXCL O_WRONLY);
use Digest::SHA;
use MIME::Base64 qw(decode_base64);

use constant READY_MARKER => "DOCS_BRIDGE_READY";
use constant COMMITTED_MARKER => "DOCS_BRIDGE_COMMITTED";
use constant ERROR_MARKER => "DOCS_BRIDGE_ERROR";
use constant MAX_RECORD_BYTES => 1024 * 1024;

sub fail {
  my ($code, $reason) = @_;
  print STDERR ERROR_MARKER . " $reason\n";
  exit $code;
}

@ARGV == 4 or fail(64, "invalid-arguments");
my ($output_path, $expected_bytes, $expected_sha256, $temporary_path) = @ARGV;
$expected_bytes =~ /^\d+$/ or fail(65, "invalid-expected-bytes");
$expected_sha256 =~ /^[a-f0-9]{64}$/ or fail(65, "invalid-expected-sha256");
for my $path ($output_path, $temporary_path) {
  $path !~ /[\0\r\n]/ or fail(65, "invalid-path");
}
(!-e $output_path and !-e $temporary_path) or fail(66, "destination-exists");

umask 0077;
sysopen(my $output, $temporary_path, O_WRONLY | O_CREAT | O_EXCL, 0600)
  or fail(67, "temporary-create-failed");
binmode($output);

my $committed = 0;
END { unlink $temporary_path unless $committed; }
$SIG{HUP} = sub { exit 129 };
$SIG{TERM} = sub { exit 143 };

system("/bin/stty", "raw", "-echo") == 0 or fail(69, "tty-required");
$| = 1;
print READY_MARKER . "\n";

my $buffer = "";
my $next_sequence = 0;
my $bytes_written = 0;
my $sha256 = Digest::SHA->new(256);

while (1) {
  my $read = sysread(STDIN, my $chunk, 64 * 1024);
  defined($read) or fail(78, "stdin-read-failed");
  $read > 0 or fail(78, "unexpected-eof");
  $buffer .= $chunk;
  length($buffer) <= MAX_RECORD_BYTES or fail(70, "record-too-large");

  while ((my $separator = index($buffer, "\x03")) >= 0) {
    my $record = substr($buffer, 0, $separator, "");
    substr($buffer, 0, 1, "");
    if ($record =~ /^D\t(\d+)\t([A-Za-z0-9+\/]*={0,2})$/) {
      my ($sequence, $payload) = ($1, $2);
      $sequence == $next_sequence or fail(70, "invalid-sequence");
      length($payload) % 4 == 0 or fail(70, "invalid-base64-length");
      my $decoded = decode_base64($payload);
      my $offset = 0;
      while ($offset < length($decoded)) {
        my $written = syswrite($output, $decoded, length($decoded) - $offset, $offset);
        defined($written) && $written > 0 or fail(71, "write-failed");
        $offset += $written;
      }
      $bytes_written += length($decoded);
      $sha256->add($decoded);
      $next_sequence += 1;
      next;
    }
    if ($record eq "C") {
      close($output) or fail(71, "close-failed");
      $bytes_written == $expected_bytes or fail(72, "byte-count-mismatch");
      my $actual_sha256 = $sha256->hexdigest;
      $actual_sha256 eq $expected_sha256 or fail(74, "sha256-mismatch");
      link($temporary_path, $output_path) or fail(75, "publish-failed");
      unlink($temporary_path) or fail(75, "temporary-cleanup-failed");
      $committed = 1;
      print COMMITTED_MARKER . " $bytes_written $actual_sha256\n";
      exit 0;
    }
    $record eq "A" and fail(76, "aborted");
    fail(77, "invalid-record");
  }
}
