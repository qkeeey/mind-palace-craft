from ultralytics import YOLO
import os
import sys


def find_all_generic_objects(image_path):
    """
    Uses standard YOLOv8 to find all 80 generic classes.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    print("Loading standard YOLOv8-Large model...")
    # We use the 'L' (Large) model for best accuracy on generic objects.
    model = YOLO('yolov8l.pt')

    # Run the prediction
    print(f"Finding generic objects in {image_path}...")
    results = model.predict(image_path, conf=0.3, verbose=False)

    # Process and display results
    result = results[0]

    if len(result.boxes) == 0:
        print("\n--- No Objects Found ---")
        return

    print(f"\n--- Found {len(result.boxes)} Generic Objects ---")

    # Loop through all detected objects
    for i, box in enumerate(result.boxes):
        class_id = int(box.cls[0])
        object_name = model.names[class_id]
        confidence = float(box.conf[0])

        print(f"Object #{i + 1}: {object_name.title()} (Confidence: {confidence:.2f})")

    # Save a new image with the objects marked
    output_filename = "generic_objects.jpg"
    print(f"\nSaving annotated image to {output_filename}...")
    annotated_image = result.plot()
    Image.fromarray(annotated_image[..., ::-1]).save(output_filename)
    print("Done!")


if __name__ == "__main__":
    image_file_path = "pdfs/"
    find_all_generic_objects(image_file_path)
