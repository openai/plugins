# How to install Temporal CLI

## macOS

### Via homebrew

```bash
brew install temporal
```

### Via tarball download

- [Darwin amd64](https://temporal.download/cli/archive/latest?platform=darwin&arch=amd64)
- [Darwin arm64](https://temporal.download/cli/archive/latest?platform=darwin&arch=arm64)

Extract any downloaded archive and add the `temporal` binary to your `PATH`.

## Linux

Homebrew (if available), Snap, or tarball download:

```bash
brew install temporal
# or
snap install temporal
```

- [Linux amd64](https://temporal.download/cli/archive/latest?platform=linux&arch=amd64)
- [Linux arm64](https://temporal.download/cli/archive/latest?platform=linux&arch=arm64)

Extract any downloaded archive and add the `temporal` binary to your `PATH`.

## Windows

Download the tarballs:

- [Windows amd64](https://temporal.download/cli/archive/latest?platform=windows&arch=amd64)
- [Windows arm64](https://temporal.download/cli/archive/latest?platform=windows&arch=arm64)

Extract the archive and add the `temporal.exe` binary to your `PATH`.

## Docker

```bash
docker run --rm temporalio/temporal --help
```

## `tcld` (Temporal Cloud CLI)

Only needed for Cloud-connected development (managing Cloud namespaces, API keys, etc.).

Homebrew:

```bash
brew install temporalio/brew/tcld
```