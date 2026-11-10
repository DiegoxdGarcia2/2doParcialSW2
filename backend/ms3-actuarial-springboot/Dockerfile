FROM eclipse-temurin:17-jre-alpine

WORKDIR /app
COPY target/ms3-actuarial-springboot-*.jar app.jar

ENV PORT=8003
EXPOSE 8003

ENTRYPOINT ["java", "-jar", "app.jar"]
