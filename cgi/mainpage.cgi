#!/usr/bin/perl

use strict;
use utf8;
use CGI;
use CGI::Cookie;
use DBI;
use lib ('/home/takahashi/perl/local/lib/perl5');
use HTML::Template;
use HTML::Entities;
use Encode;
use Data::Dumper;
use POSIX 'ceil';
binmode (STDIN,  ':utf8');
binmode (STDOUT, ':utf8');
require 'utils.cgi';
require 'timeline.pl';

sub mainpage_operator {
	# Config
	my $MAIN_PAGE_TMPL_PATH = '../tmpl/mainpage.tmpl';
	my $LOGIN_PAGE_TMPL_PATH = '../tmpl/login.tmpl';
	my $LOGIN_PAGE_CGI_PATH = 'login.cgi';
	my $invalidTweetMessage = '140文字以内で入力してください。';
	my $emptyTweetMessage = '空ツイートは投稿できません';

	# Init
	my $CGI = CGI->new();

	# Get cookie
	my $user_name =  decode_utf8($CGI->cookie('user_name'));
	my $user_password =  decode_utf8($CGI->cookie('user_password'));
	my $just_before_tweet = decode_utf8($CGI->cookie('just_before_tweet'));

	# Set head
	my $status_code = '';
	my $mode;
	if(!(defined $CGI->cookie('user_name')) || !(defined $CGI->cookie('user_password'))){
		$status_code = '200';
		$mode = 'jumpLoginPage';
	}else{
		$status_code = '200';
		$mode = 'showPage';
	}
	my @HEADER = (
			-type => 'text/html',
			-charset => "utf-8",
			-status => $status_code
		);

	# Body
	if($mode eq 'showPage'){

		# Check account
		my $user_id;
		if(($user_id = Utils::checkAccount($user_name, $user_password)) == -1){
			push @HEADER , ('-status', '400');
			print $CGI->header(@HEADER);
			return;
		}

		# Load tmpl
		my $this_page_tmpl = HTML::Template->new(filename => $MAIN_PAGE_TMPL_PATH,utf8 => 1);

		# Attach on Tweet Area
		if(defined $CGI->cookie('just_before_tweet') && $just_before_tweet ne ''){
			$this_page_tmpl->param(TWEET => HTML::Entities::encode_entities($just_before_tweet));
			# Delete cookie
			push @HEADER , ('-cookie',[new CGI::Cookie(-name=>'just_before_tweet',-value=>'')]);
		}
		if(defined $CGI->param('tweet_error')){
			$this_page_tmpl->param(IS_TWEET_ERROR => 1);
			$this_page_tmpl->param(InvalidTweetMessage => HTML::Entities::encode_entities($invalidTweetMessage));
		}elsif(defined $CGI->param('tweet_empty_error')){
			$this_page_tmpl->param(IS_TWEET_ERROR => 1);
			$this_page_tmpl->param(InvalidTweetMessage => HTML::Entities::encode_entities($emptyTweetMessage));
		}

		# Make TimeLine
		my $timeline_tmpl = makeTimeLine($CGI, '', [], $user_id, '');
		$this_page_tmpl->param('TIMELINE_TMPL' => $timeline_tmpl->output);

		# Set Header
		print $CGI->header(@HEADER), $this_page_tmpl->output;

	}elsif($mode eq 'jumpLoginPage'){

		# Add location
		push @HEADER , ('-location',$LOGIN_PAGE_CGI_PATH);

		# Set Header
		print $CGI->header(@HEADER);
	}

}

mainpage_operator();
