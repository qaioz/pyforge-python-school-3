# HTTP database

This is a super simple storage system that uses HTTP requests to store and retrieve data. 

## Idea

This is my side project. Idea for this was generated when I was working on in memory crud api. I deployed two
instances of the same application and I wanted to share data between them. I had several options to do that:

1. Use some kind of shared storage like Redis or SQL database
2. Somehow delegate post,update and delete requests to the both instances(nginx probably)
3. Create a TCP server that will store data in memory and expose it via TCP
4. Create a simple HTTP server that will store data in memory and expose it via HTTP

For now, I decided to go with the last option. I think it is simple yet challenging enough to be interesting.
Plus I will learn low to test HTTP servers, since I will be calling them from my application.

## Functionality

You should be able to create collections of specific fields and store data according to that schema.

You should be able to:

1. Create a collection
2. Delete a collection
3. Add document to a collection
4. Update documents in a collection
5. Delete documents from a collection
6. Get all documents from a collection
7. Search documents according to a specific attribute
8. Get collection size
9. Get all collections

## Implementation Insights

This will resemble a very simple file based document database. There will be no indices, no definite structure.
Every object will have just one required, unique **object_id** attribute.

To make the storage persistent (and to learn how to work with files) each collection will have associated file
where documents will be stored in JSON format.

Created collections will be stored in a separate file called **collections**.

1. **Create a collection** - add a collection name to the collections file and create a file with the same in the collections directory
2. **Delete a collection** - remove a collection name from the collections file and delete the file with the same name from the collections directory
3. **Add document to a collection** - Generate a unique id for the document and append it to the respective collection file
4. **Delete documents from a collection** - Find the document by id and remove it from the collection file
5. **Update documents in a collection** - Find the document by id and update it. Read the whole file, find the document, remove it and append the updated document
6. **Get all documents from a collection** - Read the whole file and return it
7. **Search documents according to a specific attribute** - Read the whole file and return documents that have the attribute with the specified value
8. **Get collection size** - Read the whole file and return the number of documents. (this can be optimized by storing the size in the collections file)
9. **Get all collections** - Read the collections file and return the list of collection names

## DTOs

### Collection

In out and the storage are the same

```json
{
  "name": "collection_name"
}
```

### Document

We don't want to ask for the id

#### DocumentIn
   
```json
{  
  "field1": "value1",
  "field2": "value2",
  "field3": "value3"
}  
```
   
#### DocumentOut
   
```json
{
  "object_id": "unique_id",
  "fields": {
    "field1": "value1",
    "field2": "value2",
    "field3": "value3"
  }
}
```

When we are searching for documents, we will return only the object_ids, as we might have a lot of fields
This might result in 1:n problem, that can be solved by giving the user the option to specify the fields that he wants to see,
but for now, we will return only the object_ids.

HATEOAS can be implemented by adding self links to the documents, for it to be easier to navigate to the entire document.
But for now, I will keep it simple. Client can access the document by calling the endpoint with the object_id.

#### DocumentsOut

```json
[
  {
    "object_id": "unique_id"
  },
  {
    "object_id": "unique_id"
  }
]
```

## Endpoints

Responses to post, put and delete requests should return either 200 or 400 or 404 status code, and message in the body, 
was it successful or what went wrong.

1. **POST /collection** - Create a collection
2. **DELETE /collection/{collection_name}** - Delete a collection
3. **POST /collection/{collection_name}** - Add document to a collection
4. **PUT /collection/{collection_name}/{document_id}** - Update document in a collection
5. **DELETE /collection/{collection_name}/{document_id}** - Delete document from a collection
6. **GET /collection/{collection_name}** - Get all documents from a collection
7. **GET /collection/{collection_name}/search?field=value** - Search documents according to a specific attribute(s)
8. **GET /collection/{collection_name}/size** - Get collection size
9. **GET /collections** - Get all collections

### Service Layer

1. **CreateCollection <name>** - Add an entry to the collections file and create a file with the same name in the collections directory.
If the collection already exists, return an error
2. **DeleteCollection <name>** - Delete a collection name from the collections file and delete the file with the same name from the collections directory
If the collection does not exist, return an error
3. **AddDocument <collection_name, document>** - Generate a unique id for the document and append it to the respective collection file
4. **DeleteDocument <collection_name, document_id>** - Find the document by id and remove it from the collection file
If the document does not exist, return an error
5. **UpdateDocument <collection_name, document_id, document>** - Find the document by id and update it. Read the whole file, find the document, remove it and append the updated document
If the document does not exist, return an error
6. **GetDocuments <collection_name>** - Read the whole file and return it
7. **SearchDocuments <collection_name, field, value>** - Read the whole file and return documents that have the attribute with the specified value
8. **GetCollectionSize <collection_name>** - Read the whole file and return the number of documents. (this can be optimized by storing the size in the collections file)
9. **GetCollections** - Read the collections file and return the list of collection names




