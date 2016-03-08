#!/usr/bin/env ruby

################################################################################################################################################
#
# Common Ruby Library file to include some common functions
# Function list
# => ShellOut
#
################################################################################################################################################

require 'net/http'
require 'net/https'
require "uri"
require 'json'

def ShellOut(cmd, cwd=nil)
	@command = "#{ cmd }"
	if cwd !=nil and Dir.exist?(cwd)
		puts "use #{ cwd } as current dir"
		@command = "cd #{ cwd } && #{ cmd }"
	end
	@return_value = Hash.new
	puts "run command #{ @command }"
	@return_value["output"] = `#{ @command }`
	@return_value["success"] = $?.success?
	@return_value
end

def set_params
	@params = Hash.new
	ARGV.each do|arg|
		if !arg.include?("=")
			raise "Argument Exception: Unknown arguments #{ arg }"
		end
		param = arg.split("=",2)
		@params[param[0].downcase] = param[1]
	end
	@params
end

def http_post(post_url, data, headers)
	@uri = URI.parse(post_url)
	@https = Net::HTTP.new(@uri.host,@uri.port)
	@https.use_ssl = true
	@https.post(@uri.path,data.to_json,headers)
end