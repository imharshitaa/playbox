HTTP method variants — GET/POST/PUT/DELETE/OPTIONS/PATCH, method override headers.
- Example: X-HTTP-Method-Override: DELETE

Request bodies — JSON, XML, protobuf bytes, form-data, empty body, mismatched content-type.

GraphQL — queries, mutations, introspection query, extremely deep nesting, multiple operations.

gRPC — raw protobuf wire bytes, truncated frames, unexpected field types.

Query params & path params — missing IDs, IDOR-style substitutions, arrays, encoded values.

Auth tokens — Authorization header values (Bearer/JWT), cookies, API keys in querystring.

Rate bursts / concurrency — many identical requests concurrently, replayed requests.

Accept / Accept-Encoding variations — request different formats or encodings.
