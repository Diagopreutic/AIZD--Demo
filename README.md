# **Antibiotic Inhibition Zone Detection**
This project automates the detection of antibiotic disks and their inhibition zones in Petri dish images. It measures the sizes of these zones, converts them to real-world units (millimeters), and provides an interactive interface to adjust and view the results. The goal is to simplify and speed up a key task in microbiology: determining how effective antibiotics are at stopping bacterial growth.

# **Project Overview**
In microbiology, scientists test antibiotics by placing small, round disks soaked with antibiotics onto a Petri dish covered with bacteria. If the antibiotic is effective, it stops the bacteria from growing around the disk, creating a clear circle called an inhibition zone. The bigger this zone, the more effective the antibiotic is. Traditionally, people measure these zones with a ruler, which takes time and can lead to mistakes.

## Our project uses computer vision to automate this process. Here’s what it does:

- Locates the antibiotic disks in an image of a Petri dish.

- Detects the clear inhibition zones around each disk.

- Measures the size of these zones and converts them to millimeters.

- Reads any text on the disks (like antibiotic names) using a text-recognition tool.

- Shows the results in an interactive window where users can tweak the measurements.

This saves time, reduces errors, and makes the process more consistent.





https://github.com/user-attachments/assets/9f3a3f2a-714f-4d7f-9890-ec797b8eba60





# **Approach to the Problem**

We identify small, circular antibiotic disks in the image and use their consistent 6 mm width to establish a pixel-to-millimeter scale. By examining the area around each disk, we detect the edge of the clear inhibition zone. A tool recognizes any text on the disks, and an interactive display allows users to adjust the detected zones and view updates instantly.

By splitting it up like this, the project is easier to build, test, and improve.


# **Logical Framework**

**The project follows a step-by-step logic where each part connects to the next:**

- **Disk Detection:** We use a technique called the Hough Circle Transform to find circular shapes (the disks) in the image.

- **Scale Calculation:**  We measure the disks in pixels and use their known 6 mm size to create a conversion factor from pixels to millimeters.

- **Zone Detection:** We check how bright the image is around each disk to find where the clear zone stops and the bacteria begin.

- **Text Recognition:** We zoom in on each disk and use a tool called Tesseract to read the text.

- **Interactive Display:** We use a library called OpenCV to create a window with sliders and mouse controls for users to adjust and explore the results.

This logical flow ensures the program works smoothly from start to finish.

# **Core Mechanism Explained**

**The heart of this project is figuring out the size of the inhibition zones by looking at brightness changes. Here’s how it works, explained simply:**

The inhibition zone is a bright, clear circle around the antibiotic disk where bacteria don’t grow, surrounded by darker areas where bacteria are present. To find the edge of this bright circle, we need to detect where the brightness shifts from high to low.

We begin at the center of the disk and move outward step by step, as if drawing increasingly larger circles. At each distance from the center, we examine all the pixels that form a circle at that radius and calculate their average brightness. This gives us a sense of how bright the image is at that point.

We collect these average brightness values in a list as we move further out. Inside the inhibition zone, the brightness remains high because it’s clear. But as we cross into the bacterial growth area, the brightness drops noticeably. We’re searching for a big drop in brightness—that’s the edge of the clear zone.

Imagine checking brightness at distances of 0, 2, 4, up to 150 pixels from the center. At shorter distances, the brightness is high because we’re in the clear zone. At some point—say, 50 pixels—the brightness falls sharply, indicating we’ve hit the bacterial area. That’s where the inhibition zone ends, so its radius is 50 pixels.

The actual method smooths the brightness data and uses math to precisely find the biggest drop, but the basic idea is simple: we track brightness changes outward from the center to locate the edge of the inhibition zone.

## Here’s a simplified version of how this might look in code:

**Start with an empty list to store brightness values**
```python
brightnesses = []
```

**Check brightness at increasing distances (radii)**

```python
for distance in range(0, 150, 2):  # Step by 2 pixels up to 150
    circle_pixels = get_pixels_at_distance(center, distance)  # Get pixels on the circle
    avg_brightness = sum(circle_pixels) / len(circle_pixels)  # Average brightness
    brightnesses.append(avg_brightness)  # Add to list
```

**Look for a big drop in brightness**

```python
for i in range(1, len(brightnesses)):
    if brightnesses[i] < brightnesses[i-1] - 20:  # 20 is our drop threshold
        zone_edge = 2 * i  # Distance where drop happens (times 2 because step is 2)
        break
```


**Interactive Features**
Users can adjust detected zone sizes and select specific disks through an OpenCV interface. Sliders control size adjustments, while mouse clicks enable disk selection, updating the display in real time.


![zone-2025-07-08_15 10 58](https://github.com/user-attachments/assets/ea7af4b9-9a7e-4fa2-8e08-e9e8e34b7739)




# **Mathematical Foundations**

**We use math to turn pixel measurements into real-world sizes and to find the zone edges accurately. Here’s why and how:**

- **Scale Calculation**
Images are captured in pixels, but microbiologists require measurements in millimeters. Antibiotic disks, consistently 6 mm wide, are measured in pixels to determine a scale factor. This is calculated as 6 divided by the average disk width in pixels. For example, a disk 60 pixels wide yields a scale of 0.1 mm per pixel.

- **Zone Size Calculation**
The inhibition zone’s diameter in millimeters indicates antibiotic effectiveness. The radius is measured in pixels, doubled to obtain the diameter, and multiplied by the scale factor. For instance, a 50-pixel radius with a 0.1 mm/pixel scale results in a 10 mm diameter.

- **Brightness Drop Detection**
Pinpointing the inhibition zone’s edge relies on detecting a sharp brightness decrease. Brightness values are smoothed, and the gradient is calculated to identify the point of maximum change, marking the transition from the clear zone to bacterial growth.
Identification Techniques and Tools

- **Disk Detection:** Antibiotic disks, small and circular, are identified using the Hough Circle Transform, which scans for circular shapes via edge detection.

- **Zone Detection:** Inhibition zones, bright areas around disks, are located by measuring brightness changes outward from the disk’s center, using the brightness drop method.  
Text Recognition: Labels on disks (e.g., “AMP” for ampicillin) are extracted by cropping the disk area and processing it with Tesseract OCR.



# **Conclusion**

This demo project successfully automates the detection and measurement of antibiotic inhibition zones in Petri dish images, providing microbiologists with a practical tool. Using computer vision techniques—such as the Hough Circle Transform for disk detection and brightness analysis for zone edge identification—the system ensures accurate results, converting measurements into real-world units. Interactive features, including OCR for text recognition and controls like sliders and mouse inputs, enhance usability and flexibility.Though effective, the current approach involves complex steps, such as multi-stage brightness analysis with pixel averaging and gradient detection. AI large language models (LLMs) were utilized to refine this logic, improving its robustness. Future improvements could simplify the process through streamlined image processing or machine learning-based detection. Enhancing OCR with better pre-processing or faster algorithms could also increase efficiency and accuracy.These refinements would make the tool more user-friendly and efficient, solidifying its value as a reliable solution for assessing antibiotic effectiveness in microbiology research.


This project blends image analysis, text recognition, and user interaction to make antibiotic testing faster and more precise. It’s designed so each part is clear and can be improved independently.
