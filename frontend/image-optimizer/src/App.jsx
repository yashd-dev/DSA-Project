import React, { useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Loader2, XCircle } from "lucide-react";

const Alert = ({ children, onClose }) => (
  <div
    className="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded relative flex items-center justify-between"
    role="alert"
  >
    <div className="flex items-center gap-2">
      <XCircle className="h-4 w-4" />
      <span>{children}</span>
    </div>
    {onClose && (
      <button
        onClick={onClose}
        className="text-red-500/80 hover:text-red-500 transition-colors"
      >
        <XCircle className="h-4 w-4" />
      </button>
    )}
  </div>
);

export default function ImageCompressor() {
  const [files, setFiles] = useState([]);
  const [compressedImage, setCompressedImage] = useState(null);
  const [quality, setQuality] = useState(50);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const { getRootProps, getInputProps, isFocused, isDragAccept, isDragReject } =
    useDropzone({
      accept: {
        "image/*": [".jpeg", ".jpg", ".png"],
      },
      maxFiles: 1,
      onDrop: (acceptedFiles) => {
        setError(null);
        setCompressedImage(null);
        setFiles(
          acceptedFiles.map((file) =>
            Object.assign(file, { preview: URL.createObjectURL(file) })
          )
        );
      },
    });

  const baseStyle =
    "flex flex-col items-center p-5 border-2 border-dashed bg-stone-950 text-stone-400 transition-colors";
  const focusedStyle = "border-blue-500";
  const acceptStyle = "border-green-500";
  const rejectStyle = "border-red-500";
  // For the React Dropzone component, idk uske bohot nakhre hai

  const classNames = `${baseStyle} ${isFocused ? focusedStyle : ""} ${
    isDragAccept ? acceptStyle : ""
  } ${isDragReject ? rejectStyle : ""}`;

  const handleCompression = async (e) => {
    e.preventDefault();

    if (files.length === 0) {
      setError("Please select an image first");
      return;
    }
    setCompressedImage(null);
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", files[0]);
      formData.append("quality", quality.toString());

      console.log("Sending request to server...");
      const response = await fetch("http://localhost:5000/compress/jpeg", {
        method: "POST",
        body: formData,
      });

      console.log("Response received:", response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }

      const blob = await response.blob();
      console.log("Blob received:", blob);

      const url = URL.createObjectURL(blob);
      setCompressedImage(url);
    } catch (err) {
      console.error("Compression error:", err);
      setError(`Failed to compress image: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      files.forEach((file) => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });
      if (compressedImage) {
        URL.revokeObjectURL(compressedImage);
      }
    };
  }, [files, compressedImage]);

  return (
    <>
      <div className="absolute inset-0 h-screen w-screen -z-50 body"></div>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-semibold mb-6 text-stone-100 border-b pb-4">
          Image Optimizer
        </h1>

        <div className="space-y-6">
          {error && <Alert onClose={() => setError(null)}>{error}</Alert>}

          <div {...getRootProps({ className: classNames })}>
            <input {...getInputProps()} />
            <p>Drag & drop an image here, or click to select</p>
            <p className="text-sm text-stone-500 mt-2">
              (Only *.jpeg, *.jpg and *.png images will be accepted)
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {files[0] && (
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-stone-200">Original</h3>
                <div className="border border-stone-700 rounded-lg p-2 bg-stone-900">
                  <img
                    src={files[0].preview}
                    alt="Original"
                    className="max-w-full h-auto rounded"
                    onLoad={() => URL.revokeObjectURL(files[0].preview)}
                  />
                  <p className="text-sm text-stone-400 mt-2">
                    Size: {(files[0].size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
            )}

            {compressedImage && (
              <div className="space-y-2">
                <h3 className="text-lg font-medium text-stone-200">
                  Compressed
                </h3>
                <div className="border border-stone-700 rounded-lg p-2 bg-stone-900">
                  <img
                    src={compressedImage}
                    alt="Compressed"
                    className="max-w-full h-auto rounded"
                  />
                  <a
                    href={compressedImage}
                    download="compressed-image.jpg"
                    className="text-blue-500 hover:text-blue-400 text-sm block mt-2"
                  >
                    Download compressed image
                  </a>
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-stone-200 block">
                Compression Quality: {quality}%
              </label>
              <input
                type="range"
                min="1"
                max="100"
                value={quality}
                onChange={(e) => setQuality(Number(e.target.value))}
                className="w-full h-2 bg-stone-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <button
              onClick={handleCompression}
              disabled={isLoading || files.length === 0}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center min-w-32"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Compressing...
                </>
              ) : (
                "Compress Image"
              )}
            </button>
          </div>
        </div>
      </div>{" "}
    </>
  );
}
