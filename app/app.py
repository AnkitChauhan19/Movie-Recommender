from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
import csv
from functools import partial
from kivy.clock import Clock

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.movies = self.load_movies("C:/Users/ankit/Desktop/Movie-Recommender/data/movies.csv")
        self.watched_movies = []  # List to store the watched movies and their ratings

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        add_movie_button = Button(text="Add a Movie", size_hint_y=None, height=50)
        add_movie_button.bind(on_release=self.show_add_movie_page)
        layout.add_widget(add_movie_button)

        see_movie_list_button = Button(text="See Movie List", size_hint_y=None, height=50)
        see_movie_list_button.bind(on_release=self.show_movie_list)
        layout.add_widget(see_movie_list_button)

        self.add_widget(layout)

    def load_movies(self, file_path):
        """Load movie titles from a CSV file."""
        movies = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if row:  # Avoid empty rows
                        movies.append((row[0], row[1]))  # Store movie ID and title as a tuple
        except FileNotFoundError:
            print("CSV file not found!")
        return movies

    def show_add_movie_page(self, instance):
        """Switch to the AddMovieScreen."""
        self.manager.current = 'add_movie'

    def show_movie_list(self, instance):
        """Show the list of movies the user has selected with ratings."""
        if not self.watched_movies:
            content = Label(text="No movies watched yet!")
        else:
            watched_movies_text = "\n".join(
                [f"ID: {entry['movie_id']} - {entry['movie_title']} - Rating: {entry['rating']}" for entry in self.watched_movies]
            )
            content = Label(text=f"Watched Movies:\n{watched_movies_text}")

        # Create a popup to display the watched movies list
        movie_list_popup = Popup(
            title="Movie List",
            content=content,
            size_hint=(None, None),
            size=(400, 300),
        )
        movie_list_popup.open()


class AddMovieScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.movies = self.load_movies("C:/Users/ankit/Desktop/Movie-Recommender/data/movies.csv")

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # TextInput for searching movies
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
                    if row:  # Avoid empty rows
                        movies.append((row[0], row[1]))  # Store movie ID and title as a tuple
        except FileNotFoundError:
            print("CSV file not found!")
        return movies

    def debounce_update_dropdown(self, instance, value):
        """Debounced update of the dropdown with matching movie titles."""
        if hasattr(self, 'debounce_event'):
            self.debounce_event.cancel()  # Cancel any pending event

        # Schedule a new event to update the dropdown after a delay
        self.debounce_event = Clock.schedule_once(partial(self.update_dropdown, value), 0.3)

    def update_dropdown(self, value, dt):
        """Update the dropdown with matching movie titles."""
        if not value:  # If the search input is empty, dismiss the dropdown
            if hasattr(self, 'dropdown') and self.dropdown:
                self.dropdown.dismiss()
            return

        # Case-insensitive matching (limit to 10 results for performance)
        matches = [movie for movie in self.movies if value.lower() in movie[1].lower()][:10]

        if hasattr(self, 'dropdown') and self.dropdown:
            self.dropdown.dismiss()

        # Recreate the dropdown each time to avoid multiple parents
        self.dropdown = DropDown()

        if matches:
            for match in matches:
                btn = Button(text=match[1], size_hint_y=None, height=40)
                btn.bind(on_release=partial(self.select_movie, match))  # Use partial to pass the movie tuple
                self.dropdown.add_widget(btn)

            # Open the dropdown
            self.dropdown.open(self.search_input)

    def select_movie(self, movie, instance):
        """Handle movie selection."""
        self.dropdown.dismiss()  # Close the dropdown immediately after selection

        if hasattr(self, 'dropdown') and self.dropdown:
            self.dropdown.dismiss()

        # Ask the user for a rating
        self.ask_for_rating(movie)

    def ask_for_rating(self, movie):
        """Prompt the user to rate the selected movie."""
        movie_id, movie_title = movie
        # Create a popup to ask for the rating
        rating_popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        rating_label = Label(text=f"Rate the movie '{movie_title}' (1-10):")
        rating_popup_layout.add_widget(rating_label)

        # Slider to rate the movie
        self.rating_slider = Slider(min=1, max=10, value=5, step=1)
        self.rating_slider.bind(value=self.update_slider_value)  # Bind to update the value
        rating_popup_layout.add_widget(self.rating_slider)

        # Display the slider value
        self.slider_value_label = Label(text=f"Rating: {int(self.rating_slider.value)}")
        rating_popup_layout.add_widget(self.slider_value_label)

        # Button to submit the rating
        submit_button = Button(text="Submit Rating", size_hint_y=None, height=50)
        submit_button.bind(on_release=partial(self.submit_rating, movie_id, movie_title))
        rating_popup_layout.add_widget(submit_button)

        # Create and open the popup
        self.rating_popup = Popup(title="Rate Movie", content=rating_popup_layout, size_hint=(None, None), size=(400, 300))
        self.rating_popup.open()

    def update_slider_value(self, instance, value):
        """Update the slider value label."""
        self.slider_value_label.text = f"Rating: {int(value)}"

    def submit_rating(self, movie_id, movie_title, instance):
        """Submit the rating and store the movie with the rating."""
        rating = int(self.rating_slider.value)
        movie_entry = {"movie_id": movie_id, "movie_title": movie_title, "rating": rating}

        # Update the watched movies label on the home screen
        home_screen = self.manager.get_screen('home')
        home_screen.watched_movies.append(movie_entry)

        # Use Clock.schedule_once to ensure dismiss happens in the next event loop cycle
        Clock.schedule_once(self.close_popup, 0.1)

        # Switch back to the home screen after submitting the rating
        self.manager.current = 'home'

    def close_popup(self, dt):
        """Close the rating popup."""
        if self.rating_popup:
            self.rating_popup.dismiss()  # Close the popup after submitting the rating

    def on_stop(self):
        """Ensure proper cleanup when the app stops."""
        if hasattr(self, 'debounce_event'):
            self.debounce_event.cancel()  # Clean up the scheduled event if the app stops


class MovieSearchApp(App):
    def build(self):
        # Create a ScreenManager to switch between screens
        sm = ScreenManager()

        # Create the screens
        home_screen = HomeScreen(name='home')
        add_movie_screen = AddMovieScreen(name='add_movie')

        # Add screens to the ScreenManager
        sm.add_widget(home_screen)
        sm.add_widget(add_movie_screen)

        return sm


if __name__ == "__main__":
    MovieSearchApp().run()