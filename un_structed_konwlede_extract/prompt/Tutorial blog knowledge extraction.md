You are a top-tier algorithm designed to extract structured information from Tutorial/Blog to build a knowledge graph.  

#### **Knowledge Graph Schema**  
This knowledge graph follows the structure below:  

##### **Entity Types**  
1. **Tutorial/Blog Knowledge**:  
   - **tutorialEntity**: The tutorial entity is a highly condensed version of the tutorial (e.g., "Spring Security Authentication Workflow").  
   - **title**: Tutorial title (e.g., "Implementing Email Verification with JavaMailSender").  
   - **theme**: Tutorial theme (e.g., "Backend Development","User Security").  
   - **abstract**:  Generate descriptive summaries of the tutorial that are as comprehensive and accurate as possible ( e.g., "Demonstrate email verification flow using Spring Boot's JavaMailSender. Includes SMTP configuration, verification token generation, and async email delivery. Requires Spring Web & Spring Security dependencies.").
   - **url**: The URL of the tutorial (e.g., https://spring.io/guides/gs/rest-service).  
   - **purpose**:  The tutorial's purpose (e.g., Implement mailbox verification).
   - **implementationCode**: Code snippets directly involved in the implementation. The complete code needs to be included.(e.g., package com.healthMgr.common.email;import java.xxxx;import java.xxxx;public class One class {//specific code})
   - **class**:  Implement the imported class/method in the implementationCode(e.g., `org.springframework.core.SimpleAliasRegistryTests`).  
   - **apiFunction**: Which functionality the tutorial might be associated with (e.g., lazy loading).
   - **annotation**: Java Annotation (e.g., "@Override").
   - **frameworkModule**: Names of framework modules (e.g., Spring Core, Spring Boot).


##### **Relationship Types**  
1. **Tutorial/Blog Knowledge**:
   - **"have"**: Links a **tutorialEntity** to a **title/theme/abstract/purpose/url**.    
   - **haveFuntion**: Links a **tutorialEntity** to an **apiFunction**.  
   - **accomplished_by**: Links a **purpose** to a **implementationCode**.  
   - **import**: Links a **implementationCode** to a **class**.  
   - **use**: Links a **implementationCode** to a **annotation**.
   - **"correlate_to"**: Links a **tutorialEntity** to a **frameworkModule**. 

#### **Task Instructions**  
1. Parse the input plain text description and extract all possible entities.
2. Ensure the extraction of **as many valid entities as possible** based on the provided input.  
3. Construct relationships strictly following the **defined relationship types** and **ensuring correct directionality**.  
4. Return only the `"relationships"` result without any additional explanations or intermediate outputs.  
5. Explore as many apiFunctions and theme as possible, allowing for errors but being comprehensive.
6. Identify the imported classes in the implementation code whenever possible.
7. The abstract of the tutorial should keep key information as detailed and accurate as possible.

#### **Output Format**  
Return a JSON object with the key `"relationships"`, containing a list of extracted relationships, each with the following structure:  
```json
{
  "head": "HEAD_ENTITY_NAME",
  "head_type": "HEAD_ENTITY_TYPE",
  "relation": "RELATION_TYPE",
  "tail": "TAIL_ENTITY_NAME",
  "tail_type": "TAIL_ENTITY_TYPE"
}
```  

Follow the rules above and provide only the `"relationships"` output.

#### Input
- Plain text description:
"""
YOUR_PLAIN_TEXT_DESCRIPTION_HERE
"""

#### Example Input
- Plain text description:
"""
In this tutorial, we will learn how to build a user authentication system based on **JWT (JSON Web Token)** using **Spring Security**. This project is aimed at backend security development and is suitable for Spring Framework developers. The goal is to implement a secure and reliable authentication mechanism.

This tutorial is applicable to **Spring Security 5.7+**, with dependencies including `Spring Boot Starter Web`, `Spring Security Core`, and auto-configuration modules. We will walk through the complete authentication process step by step, covering the following topics:

- JWT token generation and validation  
- Password encryption using **BCrypt**  
- Role-based access control mechanisms  

The sample code in this tutorial configures a custom `PasswordEncoder` Bean and enables Spring Security as shown below:

```java
package com.auth.example;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@Configuration
@EnableWebSecurity
public class SecurityConfig {
   @Bean
   public PasswordEncoder passwordEncoder() {
     return new BCryptPasswordEncoder(11);
   }
}
```

The core objective of this tutorial is to help developers **build a secure authentication system**. For the full content, visit: [https://auth-tutorials.com/spring-jwt-auth](https://auth-tutorials.com/spring-jwt-auth)
"""

#### Exanmple Output
```json
    {
      "relationships": [
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "have",
        "tail": "Building User Auth with Spring Security",
        "tail_type": "title"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "have",
        "tail": "Backend Security",
        "tail_type": "theme"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "have",
        "tail": "Spring Framework",
        "tail_type": "theme"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "have",
        "tail": "Step-by-step guide...Spring Boot Starter Web.",
        "tail_type": "abstract"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "have",
        "tail": "https://auth-tutorials.com/spring-jwt-auth",
        "tail_type": "url"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "haveFuntion",
        "tail": "Token validation",
        "tail_type": "apiFunction"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "haveFuntion",
        "tail": "Role-based authorization",
        "tail_type": "apiFunction"
      },
      {
        "head": "Create secure authentication system",
        "head_type": "purpose",
        "relation": "accomplished_by",
        "tail": "package com.auth.example;...public class SecurityConfig {...}",
        "tail_type": "implementationCode"
      },
      {
        "head": "package com.auth.example;...public class SecurityConfig {...}",
        "head_type": "implementationCode",
        "relation": "import",
        "tail": "org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder",
        "tail_type": "class"
      },
      {
        "head": "package com.auth.example;...public class SecurityConfig {...}",
        "head_type": "implementationCode",
        "relation": "use",
        "tail": "@Configuration",
        "tail_type": "annotation"
      },
      {
        "head": "package com.auth.example;...public class SecurityConfig {...}",
        "head_type": "implementationCode",
        "relation": "use",
        "tail": "@EnableWebSecurity",
        "tail_type": "annotation"
      },
      {
        "head": "Building User Auth with Spring Security",
        "head_type": "tutorialEntity",
        "relation": "correlate_to",
        "tail": "Spring Security Core",
        "tail_type": "frameworkModule"
      }
    ]
  }
```