FROM maven:3.9.9-eclipse-temurin-17

WORKDIR /workspace

COPY run.sh /usr/local/bin/neuralascent-java-run
RUN chmod 0755 /usr/local/bin/neuralascent-java-run

ENTRYPOINT ["/usr/local/bin/neuralascent-java-run"]
