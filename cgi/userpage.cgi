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
use DateTime;
binmode (STDIN,  ':utf8');
binmode (STDOUT, ':utf8');
require 'utils.cgi';
require 'timeline.pl';

sub userpage_operator {
	# Config
	my $USER_PAGE_TMPL_PATH = '../tmpl/userpage.tmpl';

	# Init
	my $CGI = CGI->new();

	# Get cookie
	my $user_name = decode_utf8($CGI->cookie('user_name'));
	my $user_password = decode_utf8($CGI->cookie('user_password'));

	# Get param
	my $page_user_id = decode_utf8($CGI->param('user_id'));

	# Set head
	my $status_code = '';
	my $mode;
	if(!(defined $CGI->param('user_id'))){
		$status_code = '403';
		$mode = 'fail';
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
		my $is_login = 0;
		if(defined $CGI->cookie('user_name') && defined $CGI->cookie('user_password')){
			my $user_id;
			if(($user_id = Utils::checkAccount($user_name, $user_password)) == -1){
				push @HEADER , ('-status', '400');
				print $CGI->header(@HEADER);
				return;
			}
			if($user_id == $page_user_id){
				$is_login = 1;
			}
		}

		# Load tmpl
		my $this_page_tmpl = HTML::Template->new(
			filename => $USER_PAGE_TMPL_PATH,
			utf8 => 1
		);

		# Make TimeLine
		my $WHERE = 'WHERE tweet.user_id = ?';
		my $timeline_tmpl = makeTimeLine($CGI, $WHERE, [$page_user_id], ($is_login == 1)? $page_user_id : '', '?&user_id='.$page_user_id);
		$this_page_tmpl->param('TIMELINE_TMPL' => $timeline_tmpl->output);

		# Count tweet
		my $dbh = DBI->connect('dbi:mysql:dbname=takahashi', 'www', '',{mysql_enable_utf8 => 1});
		my $sth = $dbh->prepare('SELECT COUNT(*), user.mail as mail FROM tweet LEFT JOIN user ON tweet.user_id = user.id '.$WHERE);
		$sth->execute($page_user_id);
		my $raw_count_data = $sth->fetchall_arrayref(+{});
		my $tweet_count = $raw_count_data->[0]->{'COUNT(*)'};
		$dbh->disconnect;

		# Attach tmpl
		$this_page_tmpl->param(USER_ID => HTML::Entities::encode_entities($raw_count_data->[0]->{'mail'}));
		$this_page_tmpl->param(POST_COUNT => $tweet_count);

		# Set Header
		print $CGI->header(@HEADER), $this_page_tmpl->output;

	}elsif($mode eq 'fail'){

		print $CGI->header(@HEADER);

	}

}

userpage_operator();
