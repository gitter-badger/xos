NAME = opencloud
SPECFILE = $(NAME).spec
VERSION = $(shell rpm -q --specfile $(SPECFILE) --qf '%{VERSION}\n' | head -n 1)
RELEASE = $(shell rpm -q --specfile $(SPECFILE) --qf '%{RELEASE}\n' | head -n 1)

UPLOAD_SLICE=princeton_planetstack
UPLOAD_HOST=node36.princeton.vicci.org

PWD = $(shell pwd)

dist rpm: $(NAME)-$(VERSION)-$(RELEASE).rpm

$(NAME)-$(VERSION).tar.gz:
	mkdir -p $(NAME)-$(VERSION)
	rsync -av --exclude=.svn --exclude=.git --exclude=*.tar.gz --exclude=__history --exclude=$(NAME)-$(VERSION)/ ./ $(NAME)-$(VERSION)
	tar -czf $@ $(NAME)-$(VERSION)
	rm -fr $(NAME)-$(VERSION)

$(NAME)-$(VERSION)-$(RELEASE).rpm: $(NAME)-$(VERSION).tar.gz
	mkdir -p build
	rpmbuild -bb --define '_sourcedir $(PWD)' \
                --define '_builddir $(PWD)/build' \
                --define '_srcrpmdir $(PWD)' \
                --define '_rpmdir $(PWD)' \
                --define '_build_name_fmt %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
                $(SPECFILE)

srpm: $(NAME)-$(VERSION)-$(RELEASE).src.rpm
$(NAME)-$(VERSION)-$(RELEASE).src.rpm: $(NAME)-$(VERSION).tar.gz
	rpmbuild -bs --define "_sourcedir $$(pwd)" \
                --define "_srcrpmdir $$(pwd)" \
                $(SPECFILE)

clean:
	rm -f $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)-$(RELEASE).src.rpm $(NAME)-$(VERSION)-$(RELEASE).noarch.rpm
	rm -rf build

install: $(NAME)-$(VERSION)-$(RELEASE).rpm
	scp $(NAME)-$(VERSION)-$(RELEASE).x86_64.rpm $(UPLOAD_SLICE)@$(UPLOAD_HOST):/root/
	ssh $(UPLOAD_SLICE)@$(UPLOAD_HOST) yum -y install gcc graphviz-devel graphviz-python postgresql postgresql-server python-pip python-psycopg2 libxslt-devel python-httplib2 GeoIP
	ssh $(UPLOAD_SLICE)@$(UPLOAD_HOST) rpm --install --upgrade --replacepkgs /root/$(NAME)-$(VERSION)-$(RELEASE).x86_64.rpm   
	scp /opt/planetstack/hpc_wizard/bigquery_credentials.dat /opt/planetstack/hpc_wizard/client_secrets.json $(UPLOAD_SLICE)@$(UPLOAD_HOST):/opt/planetstack/hpc_wizard/ 

.PHONY: dist

