# Image Compression App - DSA Project

This repository contains the source code for an **Image Compression App** built as part of our college's **Data Structures and Algorithms (DSA) Project**. The app compresses images, reducing file size while maintaining quality. It's divided into two main parts: a **Flask** backend and a **Vite + React** frontend.

## Project Structure

```
.
├── frontend/   # React app built with Vite
└── backend/    # Flask API for image compression
```

### Frontend (Vite + React)

The frontend is responsible for providing the user interface, where users can upload images for compression, preview the images, and download the optimized versions.

#### Key Features:
- Simple, responsive UI built using **React**.
- Users can drag and drop images for compression.
- Image preview functionality.
- Communicates with the backend via REST API.

#### Getting Started (Frontend)
1. **Navigate to the `frontend/` folder**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) to view the frontend in the browser.

### Backend (Flask)

The backend handles image compression. It exposes an API endpoint that accepts an image, compresses it, and returns the optimized version to the frontend.

#### Key Features:
- Built using **Flask**.
- Processes images via a REST API.
- Uses image processing libraries (e.g., **Pillow**, **ImageMagick**) for compression.

#### Getting Started (Backend)
1. **Navigate to the `backend/` folder**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Flask server**:
   ```bash
   flask run
   ```

6. The backend will be running at [http://localhost:5000](http://localhost:5000).

## API Endpoints

### `POST /compress`
- **Description**: Accepts an image file for compression and returns the optimized version.
- **Request**:
  - `Content-Type: multipart/form-data`
  - Payload: An image file (`image/*`)
- **Response**: The compressed image.

## How to Run the Full App

1. **Start the backend** by following the steps in the backend section.
2. **Start the frontend** by following the steps in the frontend section.
3. The frontend will automatically connect to the backend for image compression.

## Project Contributions

Feel free to contribute to this project by submitting issues, pull requests, or suggestions for improvement!