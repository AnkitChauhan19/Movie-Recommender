from recommender import get_recommendations_many, get_recommendations

many_rec = get_recommendations_many(['Inception', 'The Avengers', 'Interstellar', 'Get Out', 'CODA', 'The Truman Show', 'Iron Man', 'Thor: Ragnarok', 'Avengers: Age of Ultron', 'Captain America: Civil War'])
for i in range(len(many_rec)):
    print(many_rec[i])

rec = get_recommendations('The Avengers')
for i in range(len(rec)):
    print(rec[i])