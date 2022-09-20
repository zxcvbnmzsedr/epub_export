package cmd

import (
	"fmt"
	"github.com/bmaupin/go-epub"
	"github.com/spf13/cobra"
	"strings"
	"ztianzeng.com/epub_export/drivers/juejing"
	"ztianzeng.com/epub_export/internal/model"
	"ztianzeng.com/epub_export/internal/util"
)

var exportCmd = &cobra.Command{
	Use:   "juejing",
	Short: "export juejing to epub file",
	Args:  cobra.MinimumNArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		bookId := args[0]
		fmt.Println("掘金bookId:" + bookId)
		cookie := strings.Join(args[1:], "")
		fmt.Println("Cookie:" + cookie)
		j := juejing.Juejing{
			Platform: model.Platform{
				Cookie: cookie,
				BookId: bookId,
			},
		}
		// 获取书籍元数据
		metadata, _ := j.Metadata()
		e := epub.NewEpub(metadata.Title)
		e.SetAuthor(metadata.Author)
		e.SetLang(metadata.Lang)
		e.SetDescription(metadata.Description)
		e.AddImage(metadata.Cover, "cover")

		e.SetCover("../images/cover", "")
		for i := range metadata.Chapters {
			chapter := &metadata.Chapters[i]
			j.SectionContent(chapter)

			content, _ := util.ExtractHtmlImageToEpub(chapter.Content, e)
			e.AddSection(content, chapter.Title, "", "")
		}

		err := e.Write(metadata.Title + ".epub")
		if err != nil {

		}
	},
}

func init() {
	rootCmd.AddCommand(exportCmd)
}
