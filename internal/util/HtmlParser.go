package util

import (
	"github.com/PuerkitoBio/goquery"
	"github.com/bmaupin/go-epub"
	"github.com/gofrs/uuid"
	"strings"
)

func ExtractHtmlImageToEpub(content string, epub *epub.Epub) (string, error) {
	doc, _ := goquery.NewDocumentFromReader(strings.NewReader(content))
	doc.Find("img").Each(func(i int, selection *goquery.Selection) {
		src, exists := selection.Attr("src")
		if exists {
			f, _ := uuid.NewV4()
			fileName := f.String()
			epub.AddImage(src, fileName)
			selection.SetAttr("src", "../images/"+fileName)
		}
	})
	return doc.Html()
}
