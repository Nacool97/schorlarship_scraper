require 'open-uri'
require 'json'
require 'nokogiri'
require 'openssl'
class ScholarshipPortal
    def initialize
        #@request = HTTPClient.new()
        #file = File.open("/home/nacool/Desktop/Projects/scholarship_scraper/scholarship_url.json")
        file = File.open("/home/nakulk/pynacool/schorlarship_scraper/scholarship_url.json")
        data = JSON.load(file)
        file.close()
        @url = data[1]['url']
    end
    def get_scholarships_depth1()
        begin
        #soup = Nokogiri::HTML(URI.open(@url,{ssl_verify_mode: OpenSSL::SSL::VERIFY_NONE}))
        sch_lists = []
        for i in (1..50)
            soup = Nokogiri::HTML(URI.open(@url+i.to_s))
            data = soup.xpath('//*[@id="app"]/div[1]/div/div[2]/div/a').each do |scholarship|
                sch_details = {}
                if scholarship.css('h3').text
                sch_details['title'] = scholarship.css('h3').text
                end
                if scholarship['href']
                sch_details['url'] = "https://www.scholarshipportal.com"+scholarship['href']
                end
                if scholarship.css('div div[2] span').text
                    sch_details['scholarship_for'] = scholarship.css('div div[2] span').text
                end
                if scholarship.css('div div[3] span').text
                    sch_details['amount'] = scholarship.css('div div[3] span').text
                end
                if scholarship.css('div div[4] span').text
                    sch_details['deadline'] = scholarship.css('div div[4] span').text
                end
                sch_lists << sch_details
            end
        end
        rescue Exception => e
            puts e.message()
        end
        return sch_lists
    end
    
    def get_scholars_data(url_list)
     puts url_list[0]   
    end
    
end

if __FILE__ == $0
    obj = ScholarshipPortal.new()
    url_list = obj.get_scholarships_depth1()
    get_scholars_data(url_list) 
end