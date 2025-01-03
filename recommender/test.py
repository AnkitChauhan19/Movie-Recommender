from recommender import get_recommendations

recommendations = get_recommendations('Iron Man')
for i in range(len(recommendations)):
    print(recommendations[i][0])