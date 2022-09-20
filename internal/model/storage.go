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
}

type Chapter struct {
	Content string
	Title   string
	Id      string
}
