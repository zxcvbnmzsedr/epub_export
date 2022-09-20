package model

type Platform struct {
	Cookie string
	BookId string
}
type BookInfo struct {
	Title       string
	Author      string
	Cover       string
	Description string
	Lang        string
	Chapters    []Chapter
	CssPath     string
}

type Chapter struct {
	Content string
	Title   string
	Id      string
}
