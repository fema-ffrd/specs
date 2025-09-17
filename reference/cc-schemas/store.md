# Store

*Connection details for an external storage location (e.g., S3, Local File Server).*

## Properties

- <a id="properties/name"></a>**`name`** *(string, required)*: Human-friendly handle for the store.

  Examples:
  ```json
  "FFRD"
  ```

- <a id="properties/id"></a>**`id`** *(string, format: uuid)*: Stable identifier for the store.
- <a id="properties/store_type"></a>**`store_type`** *(string, required)*: Type of storage. Must be one of: "S3" or "LOCAL".
- <a id="properties/profile"></a>**`profile`** *(string, required)*: Credential/profile identifier used to access the store.

  Examples:
  ```json
  "account-1"
  ```

- <a id="properties/params"></a>**`params`** *(object, required)*: Store-specific parameters. Can contain additional properties.
  - <a id="properties/params/properties/root"></a>**`root`** *(string, required)*: Root path/prefix within the store. For S3, this is a bucket name and optional prefix; for Local, this is a (posix) directory path.

    Examples:
    ```json
    "model-library/ffrd-trinity"
    ```

## Examples

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

