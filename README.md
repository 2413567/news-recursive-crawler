# news-recursive-crawler
# 本项目可以递归获取新闻类网站标题及内容并支持多线程爬取
# 注意
本代码仅供学习和研究使用，不得用于非法用途。任何人或组织使用本代码造成的一切后果，与本代码作者无关。

本代码所爬取的数据应遵守相关法律法规，并尊重被爬取网站的知识产权和隐私权。如因使用本代码而引发的任何纠纷或法律问题，由使用者自行承担全部责任，作者不承担任何责任。

本代码可能存在缺陷和错误，作者无法对其准确性、及时性、完整性和实用性做出保证。使用者应自行负责对代码进行检查和测试，并对使用结果承担全部责任。

任何个人或组织在使用本代码时，若未事先获得作者的明确书面许可，则视为侵权行为，作者保留追究其法律责任的权利。
###
# 使用
域名保存在名为‘域名.xlsx’的文件中，也可手动替换参数，config.py文件可设置代理等参数。
#
结果保存在数据文件夹中，使用sqlite数据库保存。
#
运行merged.py文件可合并数据库返回结果

本代码使用Python语言实现了一个基本的网络爬虫，可以递归地抓取指定网站页面下的所有链接，并保存到SQLite数据库中。

代码包含如下模块：

- time：用于控制时间的库。
- os：用于访问操作系统功能的库。
- pandas：用于处理数据的库。
- config：自定义配置信息，包括请求头、代理、递归层数和等待时间等。
- SpiderDB：一个自定义的SQLite数据库类，用于进行数据库操作。
- requests：用于发送HTTP/HTTPS请求的库。
- lxml.etree：用于解析HTML/XML文档的库。
- functools：用于创建装饰器的库。
- urllib.parse.urljoin：用于将相对URL转换为绝对URL的函数。
- concurrent.futures.ThreadPoolExecutor：用于创建线程池的库。

其中，主要功能是递归地抓取指定网站下的所有链接。具体实现流程如下：

1. 定义一个名为`parse`的装饰器，用于解析HTML文档。该装饰器接收一个函数作为参数，并返回一个新的函数。新函数将HTML文档作为输入，并调用被装饰函数来解析HTML文档并返回结果。

2. 定义一个名为`ParseHtml`的类，用于解析HTML文档。该类包含两个解析方法：`get_src`和`get_title`。这两个方法都被`parse`装饰器修饰，用于解析HTML文档并返回结果。

3. 定义一个名为`SpiderGetResponse`的类，用于发送HTTP/HTTPS请求并获取响应数据。该类包含一个名为`get_response`的方法，用于发送请求并获取响应数据。在获取响应数据后，将请求数据和响应数据保存到SQLite数据库中。

4. 定义一个名为`get_url`的函数，用于从指定URL获取链接。该函数接收三个参数：待抓取的URL、与之相同的主机名和SQLite数据库对象。在获取页面内容后，使用`ParseHtml`类获取页面下所有链接，并根据相对路径和绝对路径转换规则将其转换为绝对路径，并将结果存储到集合对象中并去重后返回。

5. 定义一个名为`Spider`的类，用于递归地抓取指定网站下的所有链接。该类包含一个名为`recursion_url`的方法，用于递归地抓取链接。在每次递归时，该方法会从集合对象中获取所有链接，并调用`get_url`函数获取新的链接，并将其添加到集合对象中。然后，使用`SpiderDB`类将请求数据和响应数据保存到SQLite数据库中，并将递归次数减1。如果递归次数小于0，则关闭数据库连接并终止递归。

6. 在`__main__`块中创建一个名为`Spider`的实例，指定要抓取的网站主机名和协议。然后调用`recursion_url`方法开始递归抓取链接。

注意事项：

- 代码中使用了SQLite数据库来存储请求数据和响应数据。在实际应用中，可能需要根据具体情况选择适当的数据库或其他数据存储技术。
- 在获取页面下所有链接时，代码使用了相对路径和绝对路径转换规则。这些规则并不完美，因此在实际应用中可能需要根据具体情况进行修改和优化。
- 为了提高效率，代码使用了线程池来并发处理URL请求。在实际应用中，可能需要根据具体情况选择更适合的并发处理方式。
