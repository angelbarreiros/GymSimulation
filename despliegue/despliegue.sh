#!/bin/bash

echo "Starting Docker operations..."


echo "Building images..."
sudo docker buildx build -t europe-west9-docker.pkg.dev/aproxyz/aproxyz/gymbackend -f ./backend.dockerfile ..
sudo docker buildx build -t europe-west9-docker.pkg.dev/aproxyz/aproxyz/gymfrontend -f ./frontend.dockerfile ..





read -p "Do you want to push all images? (y/n) " -n 1 -r
echo    
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Pushing images..."
    sudo docker push europe-west9-docker.pkg.dev/aproxyz/aproxyz/gymbackend
    sudo docker push europe-west9-docker.pkg.dev/aproxyz/aproxyz/gymfrontend
    
    
fi

echo "Cleaning up unused images..."
sudo docker image ls --format "{{.ID}} {{.Repository}}" | awk '$2 == "<none>" {print $1}' | xargs -r sudo docker image rm --force

echo "Starting services..."
sudo docker compose up --remove-orphans



# docker rmi $(docker images -q)