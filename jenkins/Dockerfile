# ---------------------------------------------------------------------------
# Imagen de Jenkins para el cluster.
#
# Es la imagen oficial más lo que necesita nuestro Jenkinsfile:
#   - docker (solo el cliente): los builds los hace el contenedor `dind`
#     que corre al lado, en el mismo pod (ver k8s/jenkins.yaml)
#   - kubectl: para la etapa de deploy
#   - los plugins que usa el Jenkinsfile
#
# Se construye y se sube a mano (ver k8s/README.md):
#   docker buildx build --platform linux/amd64 -t guilleacq/cafeteria-jenkins:v1 --push ./jenkins
# ---------------------------------------------------------------------------

FROM jenkins/jenkins:2.580.1-lts-jdk21

USER root

COPY --from=docker:29-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:29-cli /usr/local/libexec/docker/cli-plugins /usr/local/libexec/docker/cli-plugins

# La misma versión que el cluster (1.29).
RUN curl -fsSL -o /usr/local/bin/kubectl https://dl.k8s.io/release/v1.29.15/bin/linux/amd64/kubectl \
    && chmod +x /usr/local/bin/kubectl

USER jenkins

RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    credentials-binding \
    kubernetes-cli \
    timestamper \
    junit
