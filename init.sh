#docker pull binbinxm/conda:base
docker stop iot
docker rm iot
docker run -dt \
	--restart always \
	--name iot \
	-v /home/core/home_hub:/mnt/home_hub \
	binbinxm/conda:base \
	-c "python3 /mnt/home_hub/main.py"
