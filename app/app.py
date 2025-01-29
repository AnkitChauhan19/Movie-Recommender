from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
import csv
from functools import partial
from kivy.clock import Clock
import threading
from recommender.recommender import get_recommendations_many

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.watched_movies = []

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        add_movie_button = Button(text="Add a Movie", size_hint_y=None, height=50)
        add_movie_button.bind(on_release=self.show_add_movie_page)
        layout.add_widget(add_movie_button)

        see_movie_list_button = Button(text="See Movie List", size_hint_y=None, height=50)
        see_movie_list_button.bind(on_release=self.show_movie_list)
        layout.add_widget(see_movie_list_button)

        get_recommendation_button = Button(text="Get Movie Recommendations", size_hint_y=None, height = 50)
        get_recommendation_button.bind(on_release=self.get_recommendation_page)
        layout.add_widget(get_recommendation_button)

        self.add_widget(layout)

    def show_add_movie_page(self, instance):
        """Switch to the AddMovieScreen."""
        self.manager.current = 'add_movie'

    def show_movie_list(self, instance):
        """Switch to the MovieListScreen and update its content."""
        movie_list_screen = self.manager.get_screen('movie_list')
        movie_list_screen.update_movie_list(self.watched_movies)
        self.manager.current = 'movie_list'
    
    def get_recommendation_page(self, instance):
        """Switch to the RecommendationScreen and update its content."""
        recommendation_screen = self.manager.get_screen('recommendations')
        recommendation_screen.update_recommendation(self.watched_movies)
        self.manager.current = 'recommendations'

class AddMovieScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.movies = self.load_movies("data/movies.csv")

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.search_input = TextInput(hint_text="Type movie name", size_hint_y=None, height=50)
        self.search_input.bind(text=self.debounce_update_dropdown)
        layout.add_widget(self.search_input)

        self.add_widget(layout)

    def load_movies(self, file_path):
        """Load movie titles from a CSV file."""
        movies = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if row:
                        movies.append((row[0], row[1]))
        except FileNotFoundError:
            print("CSV file not found!")
        return movies

    def debounce_update_dropdown(self, instance, value):
        """Debounced update of the dropdown with matching movie titles."""
        if hasattr(self, 'debounce_event'):
            self.debounce_event.cancel()

        self.debounce_event = Clock.schedule_once(partial(self.update_dropdown, value), 0.3)

    def update_dropdown(self, value, dt):
        """Update the dropdown with matching movie titles."""
        if not value:
            if hasattr(self, 'dropdown') and self.dropdown:
                self.dropdown.dismiss()
            return

        matches = [movie for movie in self.movies if value.lower() in movie[1].lower()][:10]

        if hasattr(self, 'dropdown') and self.dropdown:
            self.dropdown.dismiss()

        self.dropdown = DropDown()

        if matches:
            for match in matches:
                btn = Button(text=match[1], size_hint_y=None, height=40)
                btn.bind(on_release=partial(self.select_movie, match))
                self.dropdown.add_widget(btn)

            self.dropdown.open(self.search_input)

    def select_movie(self, movie, instance):
        """Handle movie selection."""
        self.dropdown.dismiss()

        if hasattr(self, 'dropdown') and self.dropdown:
            self.dropdown.dismiss()

        self.ask_for_rating(movie)

    def ask_for_rating(self, movie):
        """Prompt the user to rate the selected movie."""
        movie_id, movie_title = movie

        rating_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        rating_label = Label(text=f"Rate the movie '{movie_title}' (1-10):")
        rating_popup_layout.add_widget(rating_label)

        self.rating_slider = Slider(min=1, max=10, value=5, step=1)
        self.rating_slider.bind(value=self.update_slider_value)
        rating_popup_layout.add_widget(self.rating_slider)

        self.slider_value_label = Label(text=f"Rating: {int(self.rating_slider.value)}")
        rating_popup_layout.add_widget(self.slider_value_label)

        submit_button = Button(text="Submit Rating", size_hint_y=None, height=50)
        submit_button.bind(on_release=partial(self.submit_rating, movie_id, movie_title))
        rating_popup_layout.add_widget(submit_button)

        self.rating_popup = Popup(title="Rate Movie", content=rating_popup_layout, size_hint=(None, None), size=(400, 300))
        self.rating_popup.open()

    def update_slider_value(self, instance, value):
        """Update the slider value label."""
        self.slider_value_label.text = f"Rating: {int(value)}"

    def submit_rating(self, movie_id, movie_title, instance):
        """Submit the rating and store the movie with the rating."""
        rating = int(self.rating_slider.value)
        movie_entry = {"movie_id": movie_id, "movie_title": movie_title, "rating": rating}

        home_screen = self.manager.get_screen('home')
        home_screen.watched_movies.append(movie_entry)

        Clock.schedule_once(self.close_popup, 0.1)

        self.manager.current = 'home'

    def close_popup(self, dt):
        """Close the rating popup."""
        if self.rating_popup:
            self.rating_popup.dismiss()

    def on_stop(self):
        """Ensure proper cleanup when the app stops."""
        if hasattr(self, 'debounce_event'):
            self.debounce_event.cancel()

class MovieListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.add_widget(self.layout)

    def update_movie_list(self, watched_movies):
        """Update the screen with the list of watched movies."""
        self.layout.clear_widgets()

        if not watched_movies:
            self.layout.add_widget(Label(text="No movies watched yet!"))
        else:
            for entry in watched_movies:
                movie_info = f"ID: {entry['movie_id']} - {entry['movie_title']} - Rating: {entry['rating']}"
                self.layout.add_widget(Label(text=movie_info, size_hint_y=None, height=30))
        
        back_button = Button(text="Back to Home", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)

    def go_back(self, instance):
        """Navigate back to the home screen."""
        self.manager.current = 'home'

class RecommendationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        self.add_widget(self.layout)

    def update_recommendation(self, watched_movies):
        """Show loading indicator and start recommendation generation."""
        self.layout.clear_widgets()

        self.spinner = Spinner(text="Loading...", size_hint=(None, None), size=(100, 50))
        self.layout.add_widget(self.spinner)

        back_button = Button(text="Back to Home", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)

        threading.Thread(target=self.generate_recommendations, args=(watched_movies,), daemon=True).start()

    def generate_recommendations(self, watched_movies):
        """Generate recommendations in a separate thread."""
        if not watched_movies:
            recommendations = ["No recommendations yet!"]
        else:
            watched_movies.sort(key=lambda x: x['rating'])
            if len(watched_movies) > 10:
                watched_movies = watched_movies[:10]
            watched_movie_list = [entry['movie_title'] for entry in watched_movies]

            recommendations = get_recommendations_many(watched_movie_list)

        Clock.schedule_once(lambda dt: self.display_recommendations(recommendations))

    def display_recommendations(self, recommendations):
        """Update the UI with the recommendations."""
        self.layout.clear_widgets()

        self.layout.add_widget(Label(text="Recommendations", font_size='24sp', size_hint_y=None, height=50))
        for entry in recommendations:
            movie_info = f"{entry}"
            self.layout.add_widget(Label(text=movie_info, size_hint_y=None, height=30))

        back_button = Button(text="Back to Home", size_hint_y=None, height=50)
        back_button.bind(on_release=self.go_back)
        self.layout.add_widget(back_button)

    def go_back(self, instance):
        """Navigate back to the home screen."""
        self.manager.current = 'home'

class MovieSearchApp(App):
    def build(self):
        sm = ScreenManager()

        home_screen = HomeScreen(name='home')
        add_movie_screen = AddMovieScreen(name='add_movie')
        movie_list_screen = MovieListScreen(name='movie_list')
        recommendation_screen = RecommendationScreen(name='recommendations')

        sm.add_widget(home_screen)
        sm.add_widget(add_movie_screen)
        sm.add_widget(movie_list_screen)
        sm.add_widget(recommendation_screen)

        return sm

if __name__ == "__main__":
    MovieSearchApp().run()
