require 'open-uri'
require 'json'
require 'nokogiri'
require 'openssl'
class OpportunitiesCornerFullyFunded
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
        soup = Nokogiri::HTML(URI.open(@url,{ssl_verify_mode: OpenSSL::SSL::VERIFY_NONE}))
        verify_xpath = '//*[@id="List_of_the_Fully_Funded_Scholarships_for_International_Students_2022-2023"]'
            if !soup.xpath(verify_xpath)
                raise Exception.new('Error-In-Webpage')
            end
        
        rescue Exception => e
            puts e.message()
        end
    end
    
end

if __FILE__ == $0
    obj = OpportunitiesCornerFullyFunded.new()
    obj.get_scholarships_depth1() 
end