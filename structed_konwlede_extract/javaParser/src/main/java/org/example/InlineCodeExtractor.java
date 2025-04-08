package org.example;

import com.github.javaparser.*;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.expr.AnnotationExpr;
import com.google.gson.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

public class InlineCodeExtractor {

    static class KnowledgeGraph {
        List<Relation> relationships = new ArrayList<>();
    }

    static class Relation {
        String head;
        String headType;
        String relation;
        String tail;
        String tailType;

        public Relation(String head, String headType, String relation, String tail, String tailType) {
            this.head = head;
            this.headType = headType;
            this.relation = relation;
            this.tail = tail;
            this.tailType = tailType;
        }
    }

    static class UnstructuredInfo {
        String entityId;
        String entityType;
        String code;
        String comment;
        //String targetRelation;
        //String targetTailType;

        public UnstructuredInfo(String entityId, String entityType, String code, String comment,
                                String targetRelation, String targetTailType) {
            this.entityId = entityId;
            this.entityType = entityType;
            this.code = code;
            this.comment = comment;
            //this.targetRelation = targetRelation;
            //this.targetTailType = targetTailType;
        }
    }

    public static void main(String[] args) throws IOException {
        ParserConfiguration config = new ParserConfiguration()
                .setLanguageLevel(ParserConfiguration.LanguageLevel.JAVA_17);

        KnowledgeGraph kg = new KnowledgeGraph();
        List<UnstructuredInfo> unstructuredInfos = new ArrayList<>();
        Path projectPath = Paths.get("../spring-framework/spring-core");
        //Path projectPath = Paths.get("../spring-framework/framework-docs");
        //Path projectPath = Paths.get("../spring-framework/integration-tests");
        //Path projectPath = Paths.get("../spring-framework/spring-aop");
        //Path projectPath = Paths.get("../spring-framework/spring-aspects");
        //Path projectPath = Paths.get("../spring-framework/spring-beans");
        //Path projectPath = Paths.get("../spring-framework/spring-context");
        //Path projectPath = Paths.get("../spring-framework/spring-context-indexer");
        //Path projectPath = Paths.get("../spring-framework/spring-context-support");
        //Path projectPath = Paths.get("../spring-framework/spring-expression");
        //Path projectPath = Paths.get("../spring-framework/spring-core-test");
        //Path projectPath = Paths.get("../spring-framework/spring-instrument");
        //Path projectPath = Paths.get("../spring-framework/spring-jdbc");
        //Path projectPath = Paths.get("../spring-framework/spring-jms");
        //Path projectPath = Paths.get("../spring-framework/spring-messaging");
        //Path projectPath = Paths.get("../spring-framework/spring-orm");
        //Path projectPath = Paths.get("../spring-framework/spring-oxm");
        //Path projectPath = Paths.get("../spring-framework/spring-r2dbc");
        //Path projectPath = Paths.get("../spring-framework/spring-test");
        //Path projectPath = Paths.get("../spring-framework/spring-tx");
        //Path projectPath = Paths.get("../spring-framework/spring-web");
        //Path projectPath = Paths.get("../spring-framework/spring-webflux");
        //Path projectPath = Paths.get("../spring-framework/spring-webmvc");
        //Path projectPath = Paths.get("../spring-framework/spring-websocket");
        //Path projectPath = Paths.get("../spring-boot-main");

        // 提取模块名
        String moduleName = projectPath.getFileName().toString(); // spring-core
        // 只添加 "have" 关系
        Files.walk(projectPath)
                .filter(p -> p.toString().endsWith(".java"))
                .parallel()
                .forEach(p -> processFile(p, config, kg, unstructuredInfos, moduleName));

        Gson gson = new GsonBuilder()
                .setPrettyPrinting()
                .disableHtmlEscaping()
                .create();

        // 创建 "json" 文件夹，如果不存在
        Path structuredFolder = Paths.get("json/structured");
        Path unstructuredFolder = Paths.get("json/unstructured");
        if (!Files.exists(structuredFolder)) {
            Files.createDirectories(structuredFolder);
        }
        if (!Files.exists(unstructuredFolder)) {
            Files.createDirectories(unstructuredFolder);
        }


        try (FileWriter writer = new FileWriter(structuredFolder.resolve(moduleName + "_structured_knowledge_graph.json").toFile())) {
            gson.toJson(kg, writer);
            System.out.println(moduleName +"结构化知识图谱生成完成! 关系数: " + kg.relationships.size());
        }

        try (FileWriter writer = new FileWriter(unstructuredFolder.resolve(moduleName + "_unstructured_prompts.json").toFile())) {
            gson.toJson(unstructuredInfos, writer);
            System.out.println(moduleName +"待提取非结构化信息的提示生成完成! 提示数: " + unstructuredInfos.size());
        }
    }

    private static void processFile(Path filePath, ParserConfiguration config,
                                    KnowledgeGraph kg, List<UnstructuredInfo> unstructuredInfos, String moduleName) {
        try {
            String fullCode = Files.readString(filePath, StandardCharsets.UTF_8);
            JavaParser parser = new JavaParser(config);
            ParseResult<CompilationUnit> result = parser.parse(filePath);

            if (!result.isSuccessful()) {
                System.err.println("解析失败: " + filePath);
                result.getProblems().forEach(problem -> System.err.println(problem.getMessage()));
                return;
            }

            Optional<CompilationUnit> optionalCU = result.getResult();
            if (optionalCU.isEmpty()) {
                System.err.println("无法解析 CompilationUnit: " + filePath);
                return;
            }

            CompilationUnit cu = optionalCU.get();
            String packageName = cu.getPackageDeclaration().map(p -> p.getNameAsString()).orElse("");

            // 直接构建 module 和 package 的 "have" 关系
            if (!packageName.isEmpty()) {
                kg.relationships.add(new Relation(moduleName, "module", "has", packageName, "package"));
            }

            cu.findAll(ClassOrInterfaceDeclaration.class).forEach(cls -> {
                String className = buildClassName(packageName, cls);

                if (!packageName.isEmpty() && !cls.isAnnotationDeclaration()) {
                    kg.relationships.add(new Relation(packageName, "package", "haveClass", className, "class"));
                }

                cls.getAnnotations().forEach(anno -> {
                    kg.relationships.add(new Relation(className, "class", "use", "@"+anno.getNameAsString(), "annotation"));
                });

                addClassRelations(className, cls, fullCode, kg, unstructuredInfos);
                addFieldRelations(className, cls, kg);

                cls.getMethods().forEach(method -> {
                    addMethodRelations(className, method, fullCode, kg, unstructuredInfos);
                    method.getAnnotations().forEach(anno -> {
                        kg.relationships.add(new Relation(className + "#" + getMethodSignature(method), "method", "use",
                                "@"+anno.getNameAsString(), "annotation"));
                    });
                });

                cls.getExtendedTypes().forEach(superClass -> {
                    kg.relationships.add(new Relation(className, "class", "extend", superClass.getNameAsString(), "class"));
                });
            });

        } catch (IOException e) {
            System.err.println("文件读取错误: " + filePath);
        }
    }


    private static String buildClassName(String pkg, ClassOrInterfaceDeclaration cls) {
        return pkg.isEmpty() ? cls.getNameAsString() : pkg + "." + cls.getNameAsString();
    }

    private static void addClassRelations(String className, ClassOrInterfaceDeclaration cls,
                                          String fullCode, KnowledgeGraph kg, List<UnstructuredInfo> unstructuredInfos) {
        if (cls.isAnnotationDeclaration()) return;

        // 直接处理类成员
        String simplifiedClassCode = cls.getMembers().stream()
                .map(member -> {
                    if (member instanceof MethodDeclaration) {
                        return ((MethodDeclaration) member).toString().replaceAll("\\{\\s*}", ";"); // 移除空方法体
                    }
                    return member.toString();
                })
                .collect(Collectors.joining("\n"));

        kg.relationships.add(new Relation(className, "class", "provide", fullCode, "class_code"));

        unstructuredInfos.add(new UnstructuredInfo(className, "class", simplifiedClassCode,
                cls.getComment().map(Comment::getContent).orElse(""), "hasFunctionalDescription", "functional_description"));
    }

    private static void addFieldRelations(String className, ClassOrInterfaceDeclaration cls, KnowledgeGraph kg) {
        cls.getFields().forEach(field -> {
            field.getVariables().forEach(var -> {
                String fieldName = className + "#" + var.getNameAsString();
                kg.relationships.add(new Relation(className, "class", "haveField", fieldName, "field"));
                kg.relationships.add(new Relation(fieldName, "field", "haveType", field.getElementType().toString(), "type"));
            });
        });
    }


    private static void addMethodRelations(String className, MethodDeclaration method,
                                           String fullCode, KnowledgeGraph kg, List<UnstructuredInfo> unstructuredInfos) {
        String methodCode = method.toString().replaceAll("\\{\\s*}", ";");
        String methodId = className + "#" + getMethodSignature(method);

        kg.relationships.add(new Relation(methodId, "method", "provide", methodCode, "method_code"));
        kg.relationships.add(new Relation(className, "class", "haveMethod", methodId, "method"));

        unstructuredInfos.add(new UnstructuredInfo(methodId, "method", methodCode,
                method.getComment().map(Comment::getContent).orElse(""), "hasFunctionalDescription", "functional_description"));
    }

    private static String getMethodSignature(MethodDeclaration method) {
        return method.getNameAsString() + "(" +
                method.getParameters().stream().map(p -> p.getType().asString()).collect(Collectors.joining(",")) + ")";
    }
}

