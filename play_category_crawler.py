# -*- coding: utf-8 -*-
import os
import scrapy
import re
class GooglePlayCategoryExtractor(scrapy.Spider):
    name = 'GooglePlayCategoryExtractor'

    def start_requests(self):
        url = ''
        tag = getattr(self, 'url', None)
        if tag is not None:
            url = tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        #tp = response.xpath('//a[@itemprop="genre"]/text()').get()
        tp = response.xpath('//a[@itemprop="genre"]/@href').extract()
       	for url in tp:
       		print(str(url).split("/")[-1])
       		#for category in  str(url).split("/")[-1].split("_"):
       		#print(category)
        #print(tp.xpath('href').extract())
        