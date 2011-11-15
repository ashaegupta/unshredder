# http://instagram-engineering.tumblr.com/post/12651721845/instagram-engineering-challenge-the-unshredder

from PIL import Image

SAVE_FILE_AS = "unshredded.png"
PIXEL_DIFF = 25
PIXEL_DIFF_INCREMENT = 5
ACCURACY = 0.40

# Objects used for shred sorting. Holds a list of ordered shreds, right_most_pix_col and left_most_pix_col
class Sections(object):
    def __init__(self):
        ordered_shreds = []
        right_most_pixel_col = []
        left_most_pixel_col = []

# Unshreds a given file
class Unshredder(object):
    
    # Unshred a shredded image file
    def unshred(self):
        sections = self.sourceToSections()
        ordered_section = self.sortSections(sections)
        ordered_shreds = self.ordered_section.pop().ordered_shreds
        unshredded = self.orderedShredstoUnshreddedImage(ordered_shreds)
        unshredded.save(SAVE_FILE_AS, 'PNG')

    # Creates a list of section objects from the source image
    def sourceToSections(self):
        sections = []
        for i in range(0, self.num_columns):
           section = Section()
           section.ordered_shreds = [i]
           x = i*self.shred_width
           shred = self.image.crop((x, 0, x+self.shred_width, self.image_height))
           section.right_most_pixel_col = getPixelCol(self.shred_width-1, shred)
           section.left_most_pixel_col = getPixelCol(0, shred)
           sections.append(section)
        return sections

    # Return an image from an ordered list
    def orderedShredstoUnshreddedImage(self, ordered_shreds):
        unshredded = Image.new("RGBA", (self.image_width, self.image_height))
        curr_section = 0
        for i in ordered_shreds:
            crop_x = i*self.shred_width
            shred = self.image.crop((crop_x, 0, crop_x+self.shred_width, self.image_height))
            unshredded.paste(shred, (curr_section*self.shred_width, 0))
            curr_section += 1
        return unshredded

    # Returns a list of ordered image columns from a list of sections
    def sortSections(self, sections):
        max_number_of_runs = 10
        number_of_runs = 0
        while(len(sections)>1 and not number_of_runs>max_number_of_runs):
            sections = self.mergeSections(sections)
            number_of_runs += 1
        if (number_of_runs>max_number_of_runs):
            self.pixel_diff += PIXEL_DIFF_INCREMENT
            sections = self.getOrderedShreds(sections)
        return sections

    # Returns a list of sections that are merged as much as possible in one pass
    def mergeSections(self, sections):
        merged_list = [sections.pop(0)]
        for section in sections:
            merged_list = self.addSection(section, merged_list)
        return merged_list

    # Adds a section into the appropriate part of a list or append to end if no match
    def addSection(self, section_to_add, merged_list):
        has_match = False
        new_merged_list = []
        for section in merged_list:
            match_type = self.isSectionMatch(section, section_to_add)
            if(match_type and not has_match): 
                section = self.merge(section, section_to_add, match_type)    
                has_match = True
            new_merged_list += [section]
        if not (has_match):
            new_merged_list += [section_to_add]
        return new_merged_list

    # Merge an item on the left or right side of a section and return the adjusted section
    def merge(self, section, item, match_type):
        if(match_type==1):
            section.ordered_shreds = section.ordered_shreds + item.ordered_shreds
            section.right_most_pixel_col = item.right_most_pixel_col
        if(match_type==-1):
            section.ordered_shreds = item.ordered_shreds + section.ordered_shreds
            section.left_most_pixel_col = item.left_most_pixel_col
        return section

    # Determine if two sections match and return if right or left match
    def isSectionMatch(self, section_1, section_2):
        if self.isColumnMatch(section_1.right_most_pixel_col, section_2.left_most_pixel_col):
            return 1
        if self.isColumnMatch(section_1.left_most_pixel_col, section_2.right_most_pixel_col):
            return -1
        else:
            return 0
        
    # Determine if two columns match returns true iff all pixels meet match criteria
    def isColumnMatch(self, col_1, col_2):
        exact_pixel_matches = 0
        for i in range(0, self.image_height):
            exact_pixel_matches += self.isPixelMatch(col_1[i], col_2[i])
        if (exact_pixel_matches >= self.accuracy_threshold):
            return True
        else:
            return False

    # Determine if two pixels match
    def isPixelMatch(self, pixel_1, pixel_2):
        if ((abs(pixel_1[0] - pixel_2[0]) < self.pixel_diff) 
        and (abs(pixel_1[1] - pixel_2[1]) < self.pixel_diff)
        and (abs(pixel_1[2] - pixel_2[2]) < self.pixel_diff)):
            return 1
        else:
            return 0
        
    # Get a column of pixel
    def getPixelCol(self, col, shred):
        data = shred.getdata()
        width,height = shred.size
        pixel_col = []
        for i in range(0, height):
            pixel = data[i*width+col]
            pixel_col.append(pixel)
        return pixel_col

    # BONUS: Get number of columns in an given shredded image assuming no two images are correctly adjacent
    def getNumberOfColumns(self, pic):
        width,height = pic.size
        shred_width = 0
        i = 0
        col_1 = self.getPixelCol(i, pic)
        col_2 = self.getPixelCol(i+1, pic)
        while(self.isColumnMatch(col_1, col_2) and not i==width-1):
            col_1 = col_2
            col_2 = getPixelCol(i+1, pic)
            shred_width +=1
            i+=1
        return width/(shred_width)
    
    # Initialize unshredder
    def __init__(self, filename):
      image = Image.open(filename)
      image_width, image_height = image.size
      print image_width, image_height
      num_columns = self.getNumberOfColumns(image)
      shred_width = image_width/num_columns
      pixel_diff = PIXEL_DIFF
      accuracy_threshold = ACCURACY*image_height 
      self.unshred()
