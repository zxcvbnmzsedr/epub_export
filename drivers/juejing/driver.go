package juejing

import (
	"fmt"
	"github.com/buger/jsonparser"
	"net/http"
	"ztianzeng.com/epub_export/drivers/base"
	"ztianzeng.com/epub_export/internal/model"
)

type Juejing struct {
	model.Platform
}

func (d *Juejing) Metadata() (*model.BookInfo, error) {
	// 书籍原数据
	api := "https://api.juejin.cn/booklet_api/v1/booklet/get"
	req := base.RestyClient.R()
	req.SetHeaders(map[string]string{
		"Cookie":  d.Cookie,
		"Accept":  "application/json, text/plain, */*",
		"Referer": "https://juejin.cn/",
	})
	req.SetBody(map[string]string{
		"booklet_id": d.BookId,
	})
	res, err := req.Execute(http.MethodPost, api)
	if err != nil {
		return nil, err
	}
	baseInfo, _, _, err := jsonparser.Get(res.Body(), "data", "booklet", "base_info")
	userInfo, _, _, err := jsonparser.Get(res.Body(), "data", "booklet", "user_info")
	title, _, _, _ := jsonparser.Get(baseInfo, "title")
	coverImg, _, _, _ := jsonparser.Get(baseInfo, "cover_img")
	author, _, _, _ := jsonparser.Get(userInfo, "author")
	description, _, _, _ := jsonparser.Get(userInfo, "summary")

	var chapters []model.Chapter
	jsonparser.ArrayEach(res.Body(), func(value []byte, dataType jsonparser.ValueType, offset int, err error) {
		chapterTitle, _, _, _ := jsonparser.Get(value, "title")
		chapterId, _, _, _ := jsonparser.Get(value, "section_id")
		chapters = append(chapters, model.Chapter{
			Title: string(chapterTitle),
			Id:    string(chapterId),
		})
	}, "data", "sections")

	return &model.BookInfo{
		Title:       string(title),
		Author:      string(author),
		Cover:       string(coverImg),
		Description: string(description),
		Lang:        "zh",
		Chapters:    chapters,
	}, nil
}

func (d *Juejing) SectionContent(chapter *model.Chapter) error {
	fmt.Println("提取章节" + chapter.Title)
	u := "https://api.juejin.cn/booklet_api/v1/section/get"
	req := base.RestyClient.R()
	req.SetHeaders(map[string]string{
		"Cookie":  d.Cookie,
		"Accept":  "application/json, text/plain, */*",
		"Referer": "https://juejin.cn/",
	})
	req.SetBody(map[string]string{
		"section_id": chapter.Id,
	})
	res, err := req.Execute(http.MethodPost, u)
	if err != nil {
		return nil
	}
	content, err := jsonparser.GetString(res.Body(), "data", "section", "content")
	chapter.Content = content
	return nil
}
