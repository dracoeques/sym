
scp -r -i ./env/secrets/sym-dev-keypair.pem sym ubuntu@ec2-52-40-70-160.us-west-2.compute.amazonaws.com:src/sym-project/

scp -r -i ./env/secrets/sym-dev-keypair.pem Dockerfile ubuntu@ec2-52-40-70-160.us-west-2.compute.amazonaws.com:src/sym-project/

scp -r -i ./env/secrets/sym-dev-keypair.pem requirements.txt ubuntu@ec2-52-40-70-160.us-west-2.compute.amazonaws.com:src/sym-project/

scp -r -i ./env/secrets/sym-dev-keypair.pem setup.py ubuntu@ec2-52-40-70-160.us-west-2.compute.amazonaws.com:src/sym-project/
scp -r -i ./env/secrets/sym-dev-keypair.pem README.md ubuntu@ec2-52-40-70-160.us-west-2.compute.amazonaws.com:src/sym-project/
