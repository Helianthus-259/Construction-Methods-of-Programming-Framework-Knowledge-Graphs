### 📄 **API Documentation Generation Prompt**

**Prompt:**  
I need a detailed, Markdown-formatted API documentation for the following code snippet. Follow the structure and style guide provided to ensure accuracy and completeness.

---


### **Output Requirements:**  
#### Structure (Markdown formatted):  
```markdown
## {API_NAME}
**Purpose:** [Brief, 1-sentence description of the API functionality]  
**Signature:** `{METHOD_OR_CLASS_SIGNATURE}`

### Parameters  
| Name         | Type            | Constraints             | Description                          |
|--------------|------------------|--------------------------|--------------------------------------|
| {param_name} | {type}           | {constraints}            | {description}                        |

### Returns  
**Type:** `{RETURN_TYPE}`  
**Behavior:** [Explanation of the return value behavior, including nullability considerations]

### Lifecycle  
[Resource management details, including initialization, closure, or cleanup requirements]

### Concurrency  
[Thread-safety characteristics, reactive stream behavior (backpressure, cancellation), and any relevant synchronization concerns]

### Example  
```java
{CODE_EXAMPLE}
```

### See Also  
```
- `{RELATED_API_1}`  
- `{RELATED_API_2}`  
- `{RELATED_API_3}`
```

---

### **Style Guide:**  
- Use Javadoc-style technical terms.
- Highlight nullability with `@Nullable`.
- Use **MUST**/**MUST NOT** for mandatory constraints.
- Include reactive stream behavior such as backpressure or cancellation where applicable.
- Add `@since` tags for versioning.
- Optimize parameter constraints, error conditions, and reactive chain best practices.

---

### Example Input:  
**API Name:** UserService  
**Class/Method Code and Comments:**  
```java
/**
 * Retrieves a user by their unique ID.
 * @param userId The unique identifier of the user. Must be non-null and non-empty.
 * @return A User object if found; otherwise, null.
 * @throws UserNotFoundException if no user is found with the given ID.
 * @since 1.0
 */
public User getUserById(String userId) throws UserNotFoundException {
    // Implementation
}
```

### Example Output:  
```markdown
## UserService#getUserById
**Purpose:** Retrieves a user by their unique ID.  
**Signature:** `public User getUserById(String userId) throws UserNotFoundException`

### Parameters  
| Name     | Type    | Constraints                       | Description                       |
|----------|---------|-----------------------------------|-----------------------------------|
| userId   | String  | MUST NOT be null or empty         | The unique identifier of the user |

### Returns  
**Type:** `User`  
**Behavior:** Returns a `User` object if found; returns null if no user matches the provided ID.

### Lifecycle  
The method does not manage resource allocation beyond the scope of the call. No explicit closure required.

### Concurrency  
This method is not thread-safe. Ensure external synchronization if accessed concurrently.

### Example  
```java
try {
    User user = userService.getUserById("12345");
    System.out.println(user.getName());
} catch (UserNotFoundException e) {
    System.out.println("User not found.");
}
```

### See Also  
```
- `updateUser(User user)`  
- `deleteUser(String userId)`  
- `findAllUsers()`
```


### **Input:**  
**API Name:** `{API_NAME}`  
**Class/Method Code and Comments:**  
```java
{CODE_SNIPPET}
```
