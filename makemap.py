from PIL import Image
import os
import subprocess

# Stop from getting mad because large image
Image.MAX_IMAGE_PIXELS = None

# Download images
wgetDownload = 'wget -q --show-progress --no-parent -r -A "*.png" https://seattletransitmap.com/version/current/tiles/'
subprocess.run(wgetDownload, shell=True)

# Directory structure of output from wget
tDir = "seattletransitmap.com/version/current/tiles/"

# Get number of folders (quality levels)
numFolders = len(os.listdir(tDir))
print(f"Compiling images from quality 1 to {numFolders}")

# Loop through number of quality levels
for quality in range (1, numFolders+1, 1):
    # Input directory for each quality level
    inputDir = tDir + str(quality+8)

    # Get list of folders in input dir
    folders = sorted([f for f in os.listdir(inputDir) if os.path.isdir(os.path.join(inputDir, f))])

    # Make array to hold input tiles
    tiles = []
    tileWidth, tileHeight = 0, 0

    # Loop through folders (X position) and images (Y position)
    for folder in folders:
        # Get subfolder where images are stored. Folders iterate across X axis
        tileSubFolder = os.path.join(inputDir, folder)
        # Get image file names by listing all files in folder, add to  array only if png extension
        # Reverse sort needed because images increment up in Y direction
        tileFileNames = sorted([f for f in os.listdir(tileSubFolder) if f.endswith(".png")], reverse=True)

        # Loop through each image tile file, create a full file path, open it, then append the image data to list of tiles
        for tileFileName in tileFileNames:
            tilePath = os.path.join(tileSubFolder, tileFileName)
            tileSingle = Image.open(tilePath)
            tiles.append(tileSingle)

            # Record dimensions of single tile - should be 256x256
            if tileWidth == 0 and tileHeight == 0:
                tileWidth, tileHeight = tileSingle.size

    # Create a blank image with WxH by number of tiles * tile size
    output = Image.new("RGBA", (len(folders) * tileWidth, len(tiles) // len(folders) * tileHeight))

    # Silly line to account for zero indexed behavior
    #indexPosition = (len(folders) + 1 + (len(folders) % 2))
    # Y-indexed height of the image, in number of tiles
    tilesPerFolder = int(len(tiles) / len(folders))
    # Loop through tiles and append to output image
    for i, tile in enumerate(tiles):
        # Use floor division and modulus to get current XY coord of image. 
        # Warning: may cause headache
        # Floor division for X coord - 3 folders, 4 tiles per folder, 5 // 4 = 1 - put in second x pos
        # Modulus for Y coord - 6 % 4 = 2 - put in third y pos
        xPos = (i // tilesPerFolder) * tileWidth
        yPos = (i % tilesPerFolder) * tileHeight
        output.paste(tile, (xPos, yPos))
    
    # Remove transparent pixels
    output = output.crop(output.getbbox())

    # Save final image
    output.save(f"TransitMap {output.width}x{output.height}.png")
    # Notify users of progress to stop angry and confused users
    print(f"Saved image {quality}/{numFolders}")
