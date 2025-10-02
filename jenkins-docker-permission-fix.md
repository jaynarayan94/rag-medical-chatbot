# Jenkins in Docker: Fixing Docker Socket Permissions

When running **Jenkins inside Docker** with Docker-in-Docker (DinD), you may face:

```
permission denied while trying to connect to the Docker daemon socket
```

This happens because the `jenkins` user inside the container does not have permission to access `/var/run/docker.sock`.

---

## 🔧 Temporary Fix (per session)

1. Exit from Jenkins container if you are inside:
   ```bash
   exit
   ```

2. From the **host**, open a root shell inside the container:
   ```bash
   docker exec -u root -it jenkins-dind bash
   ```

3. Inside the container, fix the socket permissions:
   ```bash
   chown root:docker /var/run/docker.sock
   chmod 660 /var/run/docker.sock
   ```

4. Verify:
   ```bash
   ls -l /var/run/docker.sock
   ```
   Expected output:
   ```
   srw-rw---- 1 root docker 0 ... /var/run/docker.sock
   ```

5. Restart Jenkins:
   ```bash
   exit
   docker restart jenkins-dind
   ```

6. Test as `jenkins`:
   ```bash
   docker exec -u jenkins -it jenkins-dind docker ps
   ```
   ✅ Should now list running containers.

⚠️ **Note:** This fix resets on container restart since `/var/run/docker.sock` is mounted from the host.

---

## 🔒 Permanent Fix (custom image)

To avoid repeating this after every restart:

1. Create a `Dockerfile`:
   ```dockerfile
   FROM jenkins/jenkins:lts

   USER root

   # Add jenkins to docker group
   RUN groupadd -f docker \
       && usermod -aG docker jenkins

   # Fix docker.sock permissions at startup
   RUN mkdir -p /var/run \
       && chown root:docker /var/run/docker.sock \
       && chmod 660 /var/run/docker.sock

   USER jenkins
   ```

2. Build it:
   ```bash
   docker build -t jenkins-docker:lts .
   ```

3. Run it:
   ```bash
   docker run -d --name jenkins-dind \
     --privileged \
     -p 8080:8080 -p 50000:50000 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v jenkins_home:/var/jenkins_home \
     jenkins-docker:lts
   ```

Now the `jenkins` user will always have access to Docker without manual fixes. 🎉
