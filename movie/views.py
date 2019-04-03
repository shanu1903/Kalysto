from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd 
import numpy as np
from operator import itemgetter
from .forms import SearchMovie
from scipy import spatial
import operator

import os
from Rengine.settings import BASE_DIR
# file_path = os.path.join(BASE_DIR, 'movie/temp_data.csv')
url = "https://raw.githubusercontent.com/shanu1903/project_data/master/bin_part1.csv"
movies = pd.read_csv( url , encoding = 'cp1252' )

url = "https://raw.githubusercontent.com/shanu1903/project_data/master/bin_part2.csv"
bin_part2 = pd.read_csv( url , encoding = 'cp1252' )

movies  = movies.append(bin_part2)
url = "https://raw.githubusercontent.com/shanu1903/project_data/master/temp_data.csv"
bin_part2 = pd.read_csv( url , encoding = 'cp1252' )

new_id=list(range(0,movies.shape[0]))
bin_part2['new_id']=new_id
movies['new_id']=new_id
movies = movies.merge(bin_part1 , on ='new_id')

bin_part2 = 0
# movies = movies.join(bin_part1)
def Similarity(movieId1, movieId2):
    a = movies.iloc[movieId1]
    b = movies.iloc[movieId2]
    
    genresA = a['genres_bin']
    genresB = b['genres_bin']
    
    genreDistance = spatial.distance.cosine(genresA, genresB)
    
    scoreA = a['cast_bin']
    scoreB = b['cast_bin']
    scoreDistance = spatial.distance.cosine(scoreA, scoreB)
    
    directA = a['director_bin']
    directB = b['director_bin']
    directDistance = spatial.distance.cosine(directA, directB)
    
    wordsA = a['word_bin']
    wordsB = b['word_bin']
    wordsDistance = spatial.distance.cosine(directA, directB)
    return genreDistance + directDistance + scoreDistance + wordsDistance

def getNeighbors(baseMovie, K):
    distances = []

    for index, movie in movies.iterrows():
        if movie['new_id'] != baseMovie['new_id'].values[0]:
            dist = Similarity(baseMovie['new_id'].values[0], movie['new_id'])
            distances.append((movie['new_id'], dist))

    distances.sort(key=operator.itemgetter(1))
    neighbors = []

    for x in range(K):
        neighbors.append(distances[x][0])
    return neighbors

def read_data(df):
    df['genres_bin'] = df['genres_bin'].str.replace('[','').str.replace(']','')
    df['genres_bin'] = df['genres_bin'].str.split(', ')
    df['cast_bin'] = df['cast_bin'].str.replace('[','').str.replace(']','')
    df['cast_bin'] = df['cast_bin'].str.split(', ')
    df['director_bin'] = df['director_bin'].str.replace('[','').str.replace(']','')
    df['director_bin'] = df['director_bin'].str.split(', ')
    df['word_bin'] = df['word_bin'].str.replace('[','').str.replace(']','')
    df['word_bin'] = df['word_bin'].str.split(', ')
    return df
movies = read_data(movies)

def change(l1):
    l1 = list(map(int , l1))
    return l1

movies['genres_bin'] = movies['genres_bin'].apply(change)
movies['cast_bin'] = movies['cast_bin'].apply(change)
movies['director_bin'] = movies['director_bin'].apply(change)
movies['word_bin'] = movies['word_bin'].apply(change)

# Create your views here.
# def home(request):
# 	form = SearchMovie()
# 	content = {
# 		'form' : form
# 	}
# 	return render(request , 'movie/home.html' ,content)

# def autocompleteModel(request):
#     if request.is_ajax():
#         q = request.GET.get('term', '').capitalize()
#         search_qs = movies['original_title'].values.tolist()
#         # results = []
#         # print q
#         # for r in search_qs:
#         #     results.append(r.FIELD)
#         data = json.dumps(search_qs)
#     else:
#         data = 'fail'
#     mimetype = 'application/json'
#     return HttpResponse(data, mimetype)



def List(request):
	# movies1 = movies.sort_values(['original_title'])
	movies_name = movies['original_title'].values.tolist()
	movies_id = movies['id'].values.tolist()

	movies_list =zip(movies_id , movies_name , )
	# movies_list.append(movies_id)
	# movies_list.append(movies_name)
	# sorted(movies_list, key=itemgetter(1))

	content = {
		'movies_list' : movies_list
	}

	return render(request , 'movie/list.html' , content)


def detail(request , movie_id):

	base_movie = movies[movies['new_id']==movie_id]

	n = getNeighbors(base_movie, 10)

	r_movies = movies[movies['new_id'].isin(n)]
	base_name = base_movie['original_title'].values[0]
	base_date = base_movie['release_date'].values[0]
	base_cast = base_movie['cast'].str.replace('[' ,'').str.replace(']' ,'').str.replace("'" ,'').values[0]
	base_director = base_movie['director'].values[0]
	base_rating = base_movie['vote_average'].values[0]
	base_url = base_movie['url'].values[0]
	movies_name = r_movies['original_title'].values.tolist()
	movies_id = r_movies['new_id'].values.tolist()
	movies_url = r_movies['url'].values.tolist()

	movies_list =zip(movies_id , movies_name , movies_url)


	content = {
		'base_name': base_name,
		'base_date': base_date,
		'base_cast' : base_cast,
		'base_director' : base_director,
		'base_rating' : base_rating,
		'base_url' : base_url,
		'movie_id' : movie_id , 
		'movies_list' : movies_list
	}

	return render(request , 'movie/detail.html' , content)

def home(request):
	if request.method == "POST":
		form = SearchMovie(request.POST)
		if(form.is_valid()):
			name = form.cleaned_data.get('name')
			name = name.split(" ")
			name = " ".join([i[0].upper()+i[1:] for i in name])
			new_movie=movies[movies['original_title'].str.contains(name)]
			movies_name = new_movie['original_title'].values.tolist()
			movies_id = new_movie['new_id'].values.tolist()
			movies_url = new_movie['url'].values.tolist()
			movies_list =zip(movies_id , movies_name ,movies_url)
			content = {
				'result' : True,
				'movies_list' : movies_list
			}

			return render(request,'movie/result.html' , content)
	else:
		form = SearchMovie()
		content ={
			'result' : True,
			'form' : form 
		}
	form = SearchMovie()
	content = {
		'result' : True,
		'form' : form
	}

	return render(request , 'movie/home.html' , content)

