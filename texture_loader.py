import json
from texture import AnimatedTexture, FileTexture
from global_defines import *


#Load all textures specified in textures.json, they can be requested globally based on name
class TextureLoader:
    #texture directory
    directory = ""
    #dictionary of all textures
    textures = {}
    def __init__(self, tex_dir):
        self.directory = tex_dir
        #open texture list json
        with open(self.textureFilename("textures", "json")) as tex_list_file:
            tex_list = json.load(tex_list_file)
        
        #texture types contain texture size, type name, and whether texture is animated
        texture_types = {}
        for tex_type in tex_list["texture_types"]:
            #load given texture type
            texture_types[tex_type["name"]] = tex_type

        #go over all textures to load
        for tex_data in tex_list["textures"]:
            #find out type of texture
            tex_type = texture_types[tex_data["type"]]
            #get texture name
            name = tex_data["name"]
            #compute tex width and height
            w = int(tex_type["width"] * g_texture_scale)
            h = int(tex_type["height"] * g_texture_scale)
            if tex_type["animated"] == True:
                fname = self.directory + "/" + name.replace(" ", "_") + "/frame"
                frame_count = int(tex_data["frame_count"])
                texs = [FileTexture(fname + str(frame).zfill(4) + ".png") for frame in range(frame_count)]
                for t in texs: t.rescale(w, h)
                self.textures[name] = AnimatedTexture(texs, 0.01)
            else:
                #load texture by name. Filename can be found by replacing every space in name with underscore
                self.textures[name] = FileTexture(self.textureFilename(name.replace(" ", "_")))
                #rescale texture to match size given by type and UI scale
                self.textures[name].rescale(w, h)

    #find out filename of texture. Is done by prepending directory name and appending extension name, png by default.
    def textureFilename(self, tex_name, ext = "png"):
        return self.directory + "/" + tex_name + "." + ext

    #get a texture by name
    def get(self, name):
        return self.textures[name]

#load all textures
textures = TextureLoader("textures")


#if this file was ran instead of main.py, run main instead
if __name__ == "__main__":
    import main