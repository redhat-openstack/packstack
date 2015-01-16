
require 'spec_helper'

describe "choose_my_ip function" do

  let :scope do
    PuppetlabsSpec::PuppetInternals.scope
  end

  let :subject do
    function_name = Puppet::Parser::Functions.function(:choose_my_ip)
    scope.method(function_name)
  end

  context "basic unit tests" do
    before :each do
      scope.stubs(:lookupvar).with('interfaces').returns('eth0,eth1,lo')
      scope.stubs(:lookupvar).with('ipaddress_eth1').returns('1.2.3.4')
      scope.stubs(:lookupvar).with('ipaddress_eth0').returns('2.3.4.5')
      scope.stubs(:lookupvar).with('ipaddress_lo').returns('127.0.0.1')
    end

    it 'should select correct ip' do
       result = subject.call([['1.1.1.1', '2.3.4.5', '3.3.3.3']])
       result.should(eq('2.3.4.5'))
    end

    it "should raise a ParseError if there is less than 1 arguments" do
      lambda { scope.function_choose_my_ip([]) }.should(
        raise_error(Puppet::ParseError)
      )
    end

  end

end
