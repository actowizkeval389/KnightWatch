import os


def shoot():
    """Main entry point to start the UI."""
    print("🚀 Starting CodeScope UI...")
    os.system("streamlit run main.py")  # Runs Streamlit UI from the root directory


if __name__ == "__main__":
    shoot()