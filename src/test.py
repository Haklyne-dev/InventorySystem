import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image as RLImage
from reportlab.lib.units import inch

def generate_grid_pdf_from_pillow_objects(pil_images, output_pdf_path):
    """
    Takes an array of Pillow Image objects and creates a multi-column grid PDF.
    All spacings, columns, and margins are controlled via constants below.
    """
    # ==========================================
    # CHANGE THESE CONSTANTS TO CUSTOMIZE LAYOUT
    # ==========================================
    COLUMNS_COUNT = 3          # Number of columns across the page
    PAGE_SIZE     = letter     # Page size (e.g., letter, A4)
    
    # Outer page margins (distance from edge of paper to the grid)
    PAGE_MARGIN   = 0.5 * inch 
    
    # Internal cell padding (0 means images will touch side-by-side and top-to-bottom)
    CELL_PADDING_HORIZONTAL = 0   # Space between images side-by-side
    CELL_PADDING_VERTICAL   = 0   # Space between images top-to-bottom
    
    # Fixed visual height of each grid row inside the PDF
    ROW_HEIGHT    = 2.0 * inch 
    # ==========================================

    # 1. Page Dimensions Setup
    page_width, page_height = PAGE_SIZE
    printable_width = page_width - (2 * PAGE_MARGIN)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=PAGE_SIZE,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN,
        title="Customizable Grid Layout"
    )

    # Calculate exact allocation width per column
    col_width = printable_width / COLUMNS_COUNT

    # 2. Save Pillow objects temporarily for ReportLab ingestion
    temp_dir = "temp_pdf_render"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_paths = []
    formatted_images = []
    
    try:
        for i, pil_img in enumerate(pil_images):
            temp_path = os.path.join(temp_dir, f"temp_img_{i}.png")
            pil_img.save(temp_path, format="PNG")
            temp_paths.append(temp_path)
            
            # Image size calculation scales dynamically based on horizontal padding
            img_w = col_width - (CELL_PADDING_HORIZONTAL * 2)
            img_h = ROW_HEIGHT - (CELL_PADDING_VERTICAL * 2)
            
            img = RLImage(temp_path, width=img_w, height=img_h)
            img.hAlign = 'CENTER'
            formatted_images.append(img)

        # 3. Restructure into 2D Grid Rows
        grid_data = []
        for i in range(0, len(formatted_images), COLUMNS_COUNT):
            row = formatted_images[i:i + COLUMNS_COUNT]
            while len(row) < COLUMNS_COUNT:
                row.append("")  # Pad uneven rows
            grid_data.append(row)

        # 4. Create and Style Layout Table
        image_table = Table(grid_data, colWidths=[col_width] * COLUMNS_COUNT)
        image_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Apply dynamic vertical padding constraints
            ('BOTTOMPADDING', (0, 0), (-1, -1), CELL_PADDING_VERTICAL),
            ('TOPPADDING', (0, 0), (-1, -1), CELL_PADDING_VERTICAL),
            
            # Explicitly clear out ReportLab's default table padding settings
            ('LEFTPADDING', (0, 0), (-1, -1), CELL_PADDING_HORIZONTAL),
            ('RIGHTPADDING', (0, 0), (-1, -1), CELL_PADDING_HORIZONTAL),
        ]))

        # Render the PDF
        doc.build([image_table])
        
    finally:
        # 5. Guaranteed Cleanup
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

# --- Verification Block ---
if __name__ == "__main__":
    from PIL import Image
    
    # Generate 10 solid blocks to test seamless tile alignment
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'yellow', 'cyan', 'magenta', 'teal', 'gray']
    my_pillow_objects = [Image.new('RGB', (300, 200), color=c) for c in colors]
    
    generate_grid_pdf_from_pillow_objects(my_pillow_objects, "customizable_pillow_grid.pdf")
    print("Zero-margin tile grid PDF successfully generated!")
