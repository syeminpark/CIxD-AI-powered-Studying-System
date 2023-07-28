def visualize_Atlas(text,projectName):
    ids=[]
    for id in text:
        ids.append(id)
    nomic.login(os.getenv("ATLAS_TEST_API_KEY"))
    embeddings=get_embeddings(text)
    numpy_embeddings= numpy.array(embeddings)
                    
    onlineMap= atlas.map_embeddings(name='projectName',
    description= "",
    is_public = True,
    reset_project_if_exists=True,
    embeddings= numpy_embeddings,
    data=[{'id': id} for id in ids])
    print(onlineMap.maps)
    