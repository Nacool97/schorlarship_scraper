require 'open-uri'
require 'json'
require 'nokogiri'
require 'openssl'
require 'bunny'

class ScholarshipPortal
    def initialize
        #@request = HTTPClient.new()
        file = File.open("/home/nacool/Desktop/Projects/scholarship_scraper/scholarship_url.json")
        #file = File.open("/home/nakulk/pynacool/schorlarship_scraper/scholarship_url.json")
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
            break
        end
        rescue Exception => e
            puts e.message()
        end
        return sch_lists
    end
    
    def get_scholars_data(url_list)
        scholarship_lists =[]
        for url in url_list
            scholarship_details = {}
            begin
                soup = Nokogiri::HTML(URI.open(url['url']))
                if !soup
                   raise Exception.new('error-while-creating-dom')
                end
                scholarship_details['title'] = url['title']
                scholarship_details['amount'] = url['amount']
                scholarship_details['deadline'] = url['deadline']
                scholarship_details['url'] = url['url']
                scholarship_details['scholarship_for'] = url['scholarship_for']
                scholarship_details['website'] = soup.xpath('//*[@id="app"]/div[1]/div[1]/div/main/div[1]/span/a').map{|l| l['href']}[0]
                scholarship_details['description'] = soup.xpath('//*[@id="app"]/div[1]/div[1]/div/main/div[2]/p').text
                data = soup.xpath('//div[contains(@class,"content")]')
                for d in data
                    if !d.css('h2')
                        next
                    end
                    key = d.css('h2').text
                    value = d.css('p').text
                    scholarship_details[key] = value
                end

            rescue Exception =>e
                puts e.message()
            end
            scholarship_lists << scholarship_details
            
        end  
        return scholarship_lists
    end

    def queue_message(data)
        connection = Bunny.new(hostname: 'localhost')
        connection.start
        channel = connection.create_channel
        queue = channel.queue('new_data_scholarship_portal')
        puts "Message Queued"
        channel.default_exchange.publish(data, routing_key: queue.name)
        connection.close
    end
    
end

if __FILE__ == $0
    obj = ScholarshipPortal.new()
    url_list = obj.get_scholarships_depth1()
    sch_list = obj.get_scholars_data(url_list) 
    obj.queue_message(sch_list.to_json)
end