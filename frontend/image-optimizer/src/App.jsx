import React, { useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";

export default function App() {
  const [files, setFiles] = useState([]);

  const {
    acceptedFiles,
    getRootProps,
    getInputProps,
    isFocused,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    accept: "image/*",
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      setFiles(
        acceptedFiles.map((file) =>
          Object.assign(file, { preview: URL.createObjectURL(file) })
        )
      );
    },
  });

  // Styling classes
  const baseStyle =
    "flex flex-col items-center p-5 border-2 border-dashed bg-stone-950 text-stone-400 transition-colors";
  const focusedStyle = "border-blue-500";
  const acceptStyle = "border-blue-500";
  const rejectStyle = "border-red-500";

  const classNames = `${baseStyle} ${isFocused ? focusedStyle : ""} ${
    isDragAccept ? acceptStyle : ""
  } ${isDragReject ? rejectStyle : ""}`;

  // Clean up previews to avoid memory leaks
  useEffect(() => {
    return () => files.forEach((file) => URL.revokeObjectURL(file.preview));
  }, [files]);

  const thumbs = files.map((file) => (
    <div
      key={file.name}
      className="inline-flex border border-stone-600 rounded-lg p-1 mr-2 mb-2 size-52 bg-stone-900"
    >
      <div className="flex overflow-hidden">
        <img
          src={file.preview}
          alt={file.name}
          className="block w-auto h-full object-cover"
          onLoad={() => URL.revokeObjectURL(file.preview)} // Revoke after image is loaded
        />
      </div>
    </div>
  ));

  const fileList = acceptedFiles.map((file) => (
    <li key={file.path}>
      {file.path} - {file.size} bytes
    </li>
  ));

  return (
    <>
      <h1 className="mt-10 scroll-m-20 border-b pb-6 text-3xl font-semibold tracking-tight transition-colors first:mt-0">
        Welcome to Our Image Optimizer
      </h1>
      <p className="leading-7 [&:not(:first-child)]:mt-6 text-stone-300 pb-3">
        Upload your image and get the optimized version of it!
      </p>

      <div {...getRootProps({ className: classNames })}>
        <input {...getInputProps()} />
        <p>Drag 'n' drop some files here, or click to select files</p>
      </div>

      <aside className="pt-5">
        <h4 className="text-stone-300">Preview</h4>
        <div className="w-full">{thumbs}</div>
      </aside>

      <aside className="pt-5">
        <h4>Files</h4>
        <ul className="leading-7 text-stone-300 pb-3">{fileList}</ul>
      </aside>
    </>
  );
}
