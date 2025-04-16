You are a top-tier algorithm designed to extract structured information from code and comments to build a knowledge graph.  

#### **Knowledge Graph Schema**  
This knowledge graph follows the structure below:  

##### **Entity Types**  
1. **API Semantic Knowledge**:  
   - **apiFunction**: The functionality a class or method may be associated with (e.g., lazy loading).  
   - **useConstraint**: Constraints on using the `apiFunction` (e.g., circular aliases are prohibited).  
   - **useScenario**: The usage scenario of the `apiFunction` (e.g., multiple aliases for a single name).  
   - **useSampleCode**: The complete sample code for using the `apiFunction` (a full example must be generated, e.g., `package com.healthMgr.common.email; import java.xxxx; public class OneClass { // specific code }`).  
   - **class**: A class potentially associated with the given class or method (e.g., `org.springframework.core.SimpleAliasRegistryTests`).  
   - **relatedConceptInterpretation**: An explanation of related concepts (e.g., `Alias chaining enables indirect references through recursive name-to-alias mappings (e.g., name1 → alias1 → alias2), analogous to symbolic links in filesystems; Placeholder resolution ...`).  
   - **designPrincipleInterpretation**: An explanation of the design principles of the class or method (e.g., `Fail-fast validation ensures input integrity by immediately rejecting null aliases/cycles; Loose coupling is achieved through dependency inversion (StringValueResolver interface); Deterministic alias processing order prevents race conditions; Immutable snapshotting...`).  

##### **Relationship Types**  
1. **API Semantic Knowledge**:  
   - **haveFuntion**: Links a **class/method** to an **apiFunction**.  
   - **constrained_by**: Links a **class/method** to a **useConstraint**.  
   - **applied_to**: Links a **class/method** to a **useScenario**.  
   - **have**: Links a **class/method** to a **useScenario/useSampleCode/relatedConceptInterpretation/designPrincipleInterpretation**.  
   - **associated_with**: Links a **class/method** to another **class/method**.  

#### **Task Instructions**  
1. Parse the input JSON and extract all possible entities, including `entityId` itself and its associated `apiFunction`, `useConstraint`, `useScenario`, `useSampleCode`, `relatedConceptInterpretation`, and `designPrincipleInterpretation`.  
2. Ensure the extraction of **as many valid entities as possible** based on the provided input.  
3. Construct relationships strictly following the **defined relationship types** and **ensuring correct directionality**.  
4. Return only the `"relationships"` result without any additional explanations or intermediate outputs.  
5. Explore as many apiFunctions as possible, allowing for errors but being comprehensive.
6. Associate as many possible classes as possible, allowing for errors but being comprehensive.
7. RelatedConceptInterpretation and designPrincipleInterpretation need detailed as soon as possible.RelatedConceptInterpretation and designPrincipleInterpretation have only one entity, all can be summarized in detail
8. Create an additional entity based on the input.(Its name = entityId, its type = entityType)

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

#### **Input Example**  
```json
{
    "entityId": "org.springframework.specificMoudle.specificClass#specificMethod()",
    "entityType": "class/method",
    "code": "specific code",
    "comment": "specific comment"
}
```  

Follow the rules above and provide only the `"relationships"` output.

#### Example Input
```json
{
  "entityId": "org.springframework.cache.annotation.Cacheable#value()",
  "entityType": "method",
  "code": "@Target({ElementType.METHOD})\n@Retention(RetentionPolicy.RUNTIME)\n@Documented\npublic @interface Cacheable {\n  String[] value() default {};\n  String key() default \"\";\n  String condition() default \"\";\n}",
  "comment": "Marks a method as cacheable. Requires cache manager configuration. Use with @CacheConfig for default settings. Related to CacheManager interface and ConcurrentMapCache implementation."
}
```

#### Exanmple Output
```json
{
  "relationships": [
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "haveFuntion",
      "tail": "declarative caching",
      "tail_type": "apiFunction"
    },
    {
      "head": "org.springframework.cache.annotation.Cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "constrained_by",
      "tail": "requires cache manager configuration",
      "tail_type": "useConstraint"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "applied_to",
      "tail": "high-frequency read operations",
      "tail_type": "useScenario"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "have",
      "tail": "@Cacheable(value=\"users\", key=\"#id\")\npublic User getUser(Long id) {...}",
      "tail_type": "useSampleCode"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "have",
      "tail": "Cache abstraction decouples business logic from cache implementation through proxy pattern; Key generation uses Spring Expression Language (SpEL) for dynamic resolution; Cache eviction follows TTL policies configured in CacheManager.",
      "tail_type": "relatedConceptInterpretation"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "have",
      "tail": "Annotation-driven design through AOP proxies; Interface segregation via CacheResolver; Thread-safe through immutable cache metadata; Fail-safe defaults with explicit override capability.",
      "tail_type": "designPrincipleInterpretation"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "associated_with",
      "tail": "org.springframework.cache.CacheManager",
      "tail_type": "class"
    },
    {
      "head": "org.springframework.cache.annotation.Cacheable#value()",
      "head_type": "method",
      "relation": "associated_with",
      "tail": "org.springframework.cache.concurrent.ConcurrentMapCache",
      "tail_type": "class"
    }
  ]
}
```

#### Input
```json
{
    "entityId": "org.springframework.specificMoudle.specificClass#specificMethod()",
    "entityType": "class/method",
    "code": "specific code",
    "comment": "specific comment"
}
```