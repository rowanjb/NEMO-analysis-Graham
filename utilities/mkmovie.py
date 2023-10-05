import os

def mkmovie(run):

    movie_frames = "'/home/rowan/projects/rrg-pmyers-ad/rowan/NEMO-analysis-Graham/"+run+"_MLE/movie_frames/*.png'"
    movie_name = "/home/rowan/projects/rrg-pmyers-ad/rowan/NEMO-analysis-Graham/movies/"+run+"_MLE_Q.mp4"
    os.system("ffmpeg -f image2 -pattern_type glob -r 24 -i " + movie_frames + " -vcodec mpeg4 -y " + movie_name)

if __name__ == "__main__":
    for i in ['EPM155']:#['EPM151','EPM152','EPM155','EPM156','EPM157','EPM158']:
        mkmovie(run=i)
