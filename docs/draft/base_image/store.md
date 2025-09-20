# store

## Store

Connection details for an external storage location (e.g., S3, Local File Server).

### Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| name | string | Human-friendly handle for the store. | Yes |
| id | string | Stable identifier for the store. | No |
| store_type | enum: S3, FS | Type of storage. | Yes |
| profile | string | Credential/profile identifier used to access the store. | No |
| params | object | Store-specific parameters. | Yes |

#### Property Examples

- **name**: `FFRD`
- **profile**: `account-1`

#### params Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| root | string | Root path/prefix within the store. For S3, this is a bucket name and optional prefix; for Local, this is a (posix) directory path. | Yes |

##### params Examples

- **root**: `model-library/ffrd-trinity`

### Examples

#### Example 1

```json
{
  "name": "FFRD",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "store_type": "S3",
  "profile": "account-1",
  "params": {
    "root": "model-library/ffrd-trinity"
  }
}
```

