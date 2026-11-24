# Least-Privilege AWS S3 Read Policy

Use this reference only when the user requests S3 permission guidance for an
IAM Role or IAM User. Adapt placeholders to the exact resolved bucket and prefix
without broadening them.

When the prefix is empty, remove the `s3:prefix` condition and use
`arn:aws:s3:::BUCKET/*` for `GetObject`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GetBucketLocation",
      "Effect": "Allow",
      "Action": "s3:GetBucketLocation",
      "Resource": "arn:aws:s3:::BUCKET"
    },
    {
      "Sid": "ListSelectedPrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::BUCKET",
      "Condition": {
        "StringLike": { "s3:prefix": ["PREFIX", "PREFIX*"] }
      }
    },
    {
      "Sid": "ReadSelectedPrefix",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::BUCKET/PREFIX*"
    }
  ]
}
```

AWS references:

- [S3 identity-based policy examples](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html)
- [S3 policy resources and object-prefix ARNs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html)
- [Restrict `ListBucket` with `s3:prefix`](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html)
