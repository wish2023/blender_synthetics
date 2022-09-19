BLENDER_PATH='3.2/python/lib/python3.10/site-packages'
# echo $1$BLENDER_PATH
pip install -r blender_requirements.txt -t $1$BLENDER_PATH
pip install -r requirements.txt