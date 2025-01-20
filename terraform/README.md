# Tofu resources

This directory contains the Opentofu resources for the shared database. Install opentofu and aws cli to work with this.

Some useful environment variables:

AWS_PROFILE=osm_john
TF_VAR_AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
TF_VAR_db_password=please_change_me

The basic workflow is running the following from the state directory, the shared-resources directory and the postgres directory:

```
tofu init
tofu plan
tofu apply
```

An initial attempt to run this on CI using an OIDC provider to authenticate to AWS failed but could be used if this needs to be automated on Github Actions.