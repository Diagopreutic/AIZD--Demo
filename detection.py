import cv2
import numpy as np
import os
import pytesseract


# Function to find disks in the image
def detect_disks(image_path):
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray,(11,11),0)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
        param1=120, param2=25, minRadius=8, maxRadius=25
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        return [((c[0], c[1]), c[2]) for c in circles] # type: ignore
    return []


# Function to calculate the scale (mm per pixel)
def compute_scale(disk_info, disk_diamater_mm= 6.0):
    
    radii = [radius for (_,radius) in disk_info]
    
    if not radii:
        return None 
    
    avg_radius = np.mean(radii)
    scale = disk_diamater_mm / (2 * avg_radius)
    
    return scale        

# Function to find inhibition zones around disks
def detect_inhibition_zones(image_path, disk_centers):
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(12, 12))
    enhanced = clahe.apply(gray)
    blurred = cv2.medianBlur(enhanced, 11)
    
    zones = []
    
    for center in disk_centers:
        
        x ,y = center
        mask = np.zeros_like(blurred)
        cv2.circle(mask, (x, y), 150, 255, -1) # type: ignore
        roi = cv2.bitwise_and(blurred, blurred, mask=mask)
        
        
        distances = []
        intensities = []
        
        max_radius = min(150, img.shape[1] // 2, img.shape[0] // 2)
        for r in range(0, max_radius, 2):
            circle_mask = np.zeros_like(roi)
            cv2.circle(circle_mask, (x, y), r, 255, 1)  # type: ignore
            pixels = roi[circle_mask == 255]
            if pixels.size > 0:
                distances.append(r)
                intensities.append(np.median(pixels))
                
        if len(intensities) > 10:
            intensity_array = np.array(intensities, dtype=np.float32).reshape(1, -1)
            smoothed = cv2.GaussianBlur(intensity_array, (1, 5), 0).flatten()
            gradient = np.diff(smoothed)
            if gradient.size > 0:
                max_change = np.max(gradient)
                threshold = 0.8 * max_change
                change_points = np.where(gradient > threshold)[0]
                if change_points.size > 0:
                    zone_radius = distances[change_points[0]]
                    zones.append((center, zone_radius))        
            
    return zones 


# Function to perform OCR on a disk region
def ocr_disk(image, center, radius):
    x, y = center
    crop_size = int(radius * 1.5)
    crop = image[max(y - crop_size, 0):min(y + crop_size, image.shape[0]),
                 max(x - crop_size, 0):min(x + crop_size, image.shape[1])]
    if crop.size == 0:
        return "No text"
    if len(crop.shape) == 3:
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(crop, config='--psm 6')
    return text.strip() if text.strip() else "No text"


# Mouse callback function for selecting circles
def on_mouse_click(event, x, y, flags, param):
    global selected_index
    if event == cv2.EVENT_LBUTTONDOWN:
        for i, (center, _) in enumerate(inhibition_zones):
            adjusted_radius = original_radii[i] * scaling_factors[i]
            distance = np.sqrt((x - center[0])**2 + (y - center[1])**2)
            if distance < adjusted_radius:
                selected_index = i
                cv2.setTrackbarPos('Radius Multiplier (%)', 'Inhibition Zones', int(scaling_factors[i] * 100))
                break
        else:
            selected_index = -1  # Deselect if clicked outside
            
            


# Main workflow
image_path = "/media/drunk/HOLLOW/1 Priority/002 Work/Internship/Diagopreutic/Task -2/Demo/Images/Screenshot from 2025-06-30 12-53-10.png"
if not os.path.exists(image_path):
    print(f"Error: Image file '{image_path}' not found!")
else:
    # Detect disks
    disks = detect_disks(image_path)
    if not disks:
        print("No disks found in the image.")
    else:
        # Calculate scale
        scale = compute_scale(disks)
        if scale is None:
            print("Could not calculate scale.")
        else:
            # Get disk centers
            centers = [center for (center, _) in disks]
            # Detect inhibition zones
            inhibition_zones = detect_inhibition_zones(image_path, centers)
            print(f"Found {len(inhibition_zones)} inhibition zones.")
            
            # Apply OCR to each disk
            img = cv2.imread(image_path)
            disk_texts = [ocr_disk(img, center, radius) for center, radius in disks]
            
            # Initialize variables for individual circle adjustment
            original_radii = [radius for _, radius in inhibition_zones]
            scaling_factors = [1.0] * len(inhibition_zones)
            selected_index = -1
            
            # Create OpenCV window and trackbar
            cv2.namedWindow('Inhibition Zones')
            cv2.createTrackbar('Radius Multiplier (%)', 'Inhibition Zones', 100, 200, lambda x: None)
            cv2.setTrackbarPos('Radius Multiplier (%)', 'Inhibition Zones', 100)  # Default 100%
            cv2.setMouseCallback('Inhibition Zones', on_mouse_click)
            
            while True:
                # Get slider value
                multiplier = cv2.getTrackbarPos('Radius Multiplier (%)', 'Inhibition Zones') / 100.0
                if selected_index != -1:
                    scaling_factors[selected_index] = multiplier
                display_img = img.copy()
                
                # Draw circles and text
                for i, (center, _) in enumerate(inhibition_zones):
                    adjusted_radius = int(original_radii[i] * scaling_factors[i])
                    color = (0, 255, 0) if i != selected_index else (255, 0, 0)  # Green or blue
                    thickness = 2 if i != selected_index else 3
                    cv2.circle(display_img, center, adjusted_radius, color, thickness)
                    cv2.circle(display_img, center, 5, (0, 0, 255), -1)  # Red center dot
                    diameter_mm = (2 * adjusted_radius) * scale
                    cv2.putText(display_img, disk_texts[i], (center[0] - 30, center[1] - adjusted_radius - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # OCR text
                    cv2.putText(display_img, f"{diameter_mm:.2f} mm", (center[0] - 30, center[1] + adjusted_radius + 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  # Diameter
                
                # Display image
                cv2.imshow('Inhibition Zones', display_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cv2.destroyAllWindows()