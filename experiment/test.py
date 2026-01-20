import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject,
    TextStringObject,
    ArrayObject,
    FloatObject,
    DictionaryObject,
)

# Input / output
input_pdf = r"C:\Users\dsouz\Downloads\A_Novel_Integrated_Approach_for_Stock_Prediction_Based_on_Modal_Decomposition_Technology_and_Machine_Learning.pdf"
output_pdf = r"output_highlighted.pdf"
target_sentences = [
    "After the COVID-19 ended,",
    "Machine learning improves healthcare"
]

reader = PdfReader(input_pdf)
writer = PdfWriter()

with pdfplumber.open(input_pdf) as pdf:
    for page_number, plumb_page in enumerate(pdf.pages):
        page = reader.pages[page_number]
        highlights = []

        # extract all words with their bbox
        words = plumb_page.extract_words()

        for target in target_sentences:
            # find consecutive words that match target sentence
            for i in range(len(words)):
                sentence_words = []
                j = i
                text_accum = ""
                while j < len(words) and len(text_accum) < len(target):
                    sentence_words.append(words[j])
                    text_accum += words[j]["text"] + " "
                    j += 1

                if target.strip() in text_accum.strip():
                    # compute rectangle covering all matched words
                    x0 = min(w["x0"] for w in sentence_words)
                    top = min(w["top"] for w in sentence_words)
                    x1 = max(w["x1"] for w in sentence_words)
                    bottom = max(w["bottom"] for w in sentence_words)

                    # PDF coordinate system
                    height = plumb_page.height
                    rect = (x0, height - bottom, x1, height - top)

                    highlights.append(rect)

        # add annotation for each highlight
        for rect in highlights:
            x0, y0, x1, y1 = rect
            annot = DictionaryObject()
            annot.update({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Highlight"),
                NameObject("/Rect"): ArrayObject([FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y1)]),
                NameObject("/Contents"): TextStringObject("Auto highlight"),
                NameObject("/C"): ArrayObject([FloatObject(1), FloatObject(1), FloatObject(0)]),
                NameObject("/QuadPoints"): ArrayObject([FloatObject(x0), FloatObject(y1), FloatObject(x1), FloatObject(y1),
                                                        FloatObject(x0), FloatObject(y0), FloatObject(x1), FloatObject(y0)])
            })
            if "/Annots" in page:
                page["/Annots"].append(annot)
            else:
                page[NameObject("/Annots")] = ArrayObject([annot])

        writer.add_page(page)

# save highlighted PDF
with open(output_pdf, "wb") as f:
    writer.write(f)