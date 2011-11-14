# http://instagram-engineering.tumblr.com/post/12651721845/instagram-engineering-challenge-the-unshredder
# Full solution, with bonus at end

from PIL import Image

PIXEL_DIFF = 25
PIXEL_DIFF_INCREMENT = 5
IMAGE_HEIGHT = 359
IMAGE_WIDTH = 640
SHRED_WIDTH = 32
NUMBER_OF_COLUMNS = IMAGE_WIDTH/SHRED_WIDTH
ACCURACY = 0.40
ACCURACY_INCREMENT = -0.05
ACCURACY_THRESHOLD = ACCURACY*IMAGE_HEIGHT

# Unshred a shredded image file
def unshred(file_name):
    image = Image.open(file_name)
    sections = sourceToSections(image)
    ordered_sections = getOrderedShreds(sections, ACCURACY_THRESHOLD, PIXEL_DIFF)
    ordered_shreds = ordered_sections.pop().ordered_shreds
    unshredded = orderedShredstoUnshredded(ordered_shreds, image)
    unshredded.save('unshredded.png', 'PNG')

# Class to keep track of an ordered list of shreds, right_most_pix_col and left_most_pix_col
class Section(object):
    def __init__(self):
        ordered_shreds = []
        right_most_pixel_col = []
        left_most_pixel_col = []

# Creates a list of section objects from the source image
def sourceToSections(image):
    sections = []
    for i in range(0, NUMBER_OF_COLUMNS):
       section = Section()
       section.ordered_shreds = [i]
       x = i*SHRED_WIDTH
       shred = image.crop((x, 0, x+SHRED_WIDTH, IMAGE_HEIGHT))
       section.right_most_pixel_col = getPixelCol(SHRED_WIDTH-1, shred)
       section.left_most_pixel_col = getPixelCol(0, shred)
       sections.append(section)
    return sections

# Return an image from an ordered list
def orderedShredstoUnshredded(ordered_shreds, image):
    unshredded = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT))
    print ordered_shreds
    curr_section = 0
    for i in ordered_shreds:
        crop_x = i*SHRED_WIDTH
        shred = image.crop((crop_x, 0, crop_x+SHRED_WIDTH, IMAGE_HEIGHT))
        unshredded.paste(shred, (curr_section*SHRED_WIDTH, 0))
        curr_section += 1  
    return unshredded

# Returns a list of ordered image columns from a list of sections
def getOrderedShreds(sections, accuracy_threshold, pixel_diff):
    max_number_of_runs = 10
    number_of_runs = 0
    while(len(sections)>1 and not number_of_runs>max_number_of_runs):
        sections = mergeSections(sections, accuracy_threshold, pixel_diff)
        number_of_runs += 1
    if (number_of_runs>max_number_of_runs):
        accuracy_threshold += ACCURACY_INCREMENT
        pixel_diff += PIXEL_DIFF_INCREMENT
        sections = getOrderedShreds(sections, accuracy_threshold, pixel_diff)
    return sections

# Returns a list of sections that are merged as much as possible in one pass
def mergedSections(sections, accuracy_threshold, pixel_diff):
    merged_list = [sections.pop(0)]
    for section in sections:
        merged_list = addSection(section, merged_list, accuracy_threshold, pixel_diff)
    return merged_list

# Adds a section into the appropriate part of a list or append to end if no match
def addSection(section_to_add, merged_list, accuracy_threshold, pixel_diff):
    has_match = False
    new_merged_list = []
    for section in merged_list:
        match_type = isSectionMatch(section, section_to_add, accuracy_threshold, pixel_diff)
        if(match_type and not has_match): 
            section = merge(section, section_to_add, match_type)    
            has_match = True
        new_merged_list += [section]
    if not (has_match):
        new_merged_list += [section_to_add]
    return new_merged_list

# Merge an item on the left or right side of a section and return the adjusted section
def merge(section, item, match_type):
    if(match_type==1):
        section.ordered_shreds = section.ordered_shreds + item.ordered_shreds
        section.right_most_pixel_col = item.right_most_pixel_col
    if(match_type==-1):
        section.ordered_shreds = item.ordered_shreds + section.ordered_shreds
        section.left_most_pixel_col = item.left_most_pixel_col
    return section

# Determine if two sections match and return if right or left match
def isSectionMatch(section_1, section_2, accuracy_threshold, pixel_diff):
    if isColumnMatch(section_1.right_most_pixel_col, section_2.left_most_pixel_col,
                    accuracy_threshold, pixel_diff):
        return 1
    if isColumnMatch(section_1.left_most_pixel_col, section_2.right_most_pixel_col,
                    accuracy_threshold, pixel_diff):
        return -1
    else:
        return 0
        
# Determine if two columns match returns true iff all pixels meet match criteria
def isColumnMatch(col_1, col_2, accuracy_threshold, pixel_diff):
    exact_pixel_matches = 0
    for i in range(0, IMAGE_HEIGHT):
        exact_pixel_matches += isPixelMatch(col_1[i], col_2[i], pixel_diff)
    if (exact_pixel_matches >= accuracy_threshold):
        return True
    else:
        return False

# Determine if two pixels match
def isPixelMatch(pixel_1, pixel_2, pixel_diff):
    if ((abs(pixel_1[0] - pixel_2[0]) < pixel_diff) 
    and (abs(pixel_1[1] - pixel_2[1]) < pixel_diff)
    and (abs(pixel_1[2] - pixel_2[2]) < pixel_diff)):
        return 1
    else:
        return 0
        
# Get a column of pixel
def getPixelCol(col, shred):
    data = shred.getdata()
    width,height = shred.size
    pixel_col = []
    for i in range(0, height):
        pixel = data[i*width+col]
        pixel_col.append(pixel)
    return pixel_col

# BONUS: Get number of columns in an given shredded image assuming no two images are correctly adjacent
def getNumberOfColumns(image):
    width,height = image.size
    shred_width = 0
    i = 0
    col_1 = getPixelCol(i, image)
    col_2 = getPixelCol(i+1, image)
    while(isColumnMatch(col_1, col_2, ACCURACY_THRESHOLD, PIXEL_DIFF) and not i==width-1):
        col_1 = col_2
        col_2 = getPixelCol(i+1, image)
        shred_width +=1
        i+=1
    return width/(shred_width)
        